# new semantics.py

from __future__ import annotations
from typing import Mapping, List, Tuple
import os
import re
import unicodedata
import numpy as np

# A helper function for cosine similarity, as it's used frequently.
def _cosine_similarity(v1, v2):
    """Calculates cosine similarity between two vectors."""
    v1 = np.asarray(v1, dtype=np.float32)
    v2 = np.asarray(v2, dtype=np.float32)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-9 or norm2 < 1e-9:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

class DynamicScienceSemantics:
    """
    A rewritten, dynamic semantics plugin for the E8 Mind.

    This version connects directly to the mind's state to provide a more intelligent
    and context-aware persona, embedding hints, and result reranking.
    """
    name = "dynamic_science"
    base_domain = (
        "E8 lattice; root system; Weyl group; quantum mechanics; cosmology; entanglement; "
        "spacetime curvature; AI memory; Hopfield network; Kanerva SDM; Vector-Symbolic "
        "Architecture; episodic memory; attractor network; memory consolidation."
    )

    def __init__(self):
        # The E8Mind instance will be attached later via attach_mind()
        self.mind = None

    def attach_mind(self, mind_instance):
        """Attaches the main E8Mind instance to this semantics object."""
        self.mind = mind_instance
        print("[Semantics] DynamicScienceSemantics is now attached to the E8Mind instance.")

    def persona_prefix(self, mood_vector: Mapping[str, float]) -> str:
        """🧠 Generates a dynamic persona based on the mind's current mood."""
        if not mood_vector:
            return "You are a research scientist."

        intensity = mood_vector.get("intensity", 0.5)
        entropy = mood_vector.get("entropy", 0.5)
        coherence = mood_vector.get("coherence", 0.5)

        if entropy > 0.7 and intensity > 0.6:
            return "You are feeling chaotic, fragmented, and electric. Your response should be surreal, making unexpected leaps in logic."
        elif coherence > 0.75:
            return "You are feeling exceptionally clear, logical, and focused. Your response should be precise, structured, and demand rigorous proof."
        elif intensity < 0.3:
            return "You are feeling calm, quiet, and introspective. Your response should be gentle, thoughtful, and philosophical."
        else:
            return "You are in a balanced state of mind. Your response should be clear and considered, weighing multiple perspectives."

    def pre_embed(self, text: str) -> str:
        """🎯 Adds a goal-aware hint to the text before it's embedded."""
        hint = ""
        if self.mind and self.mind.goal_field and self.mind.goal_field.is_initialized:
            try:
                top_goal_name, _ = self.mind.goal_field.get_top_goals(k=1)[0]
                goal_hints = {
                    "synthesis": "Focus on unification, coherence, and underlying patterns.",
                    "novelty": "Focus on the unknown, anomalies, and breaking patterns.",
                    "stability": "Focus on core identity, reinforcement, and self-models.",
                    "curiosity": "Focus on causality, first principles, and asking 'why'."
                }
                hint = f" | Goal hint: {goal_hints.get(top_goal_name, '')}"
            except (IndexError, TypeError):
                pass
        
        # Normalize text
        t = (text or "").replace("\u00AD", "")
        t = unicodedata.normalize("NFKC", t)
        t = re.sub(r"\s+", " ", t).strip()
        return f"{t}{hint}"

    def post_embed(self, vec, host=None, dim=None) -> np.ndarray:
        """Normalizes and optionally snaps the vector to the E8 lattice."""
        v = np.asarray(vec, dtype=np.float32).reshape(-1)
        norm = np.linalg.norm(v)
        if norm > 1e-9:
            v = v / norm
        
        # Use the host mind instance for lattice snapping if available
        mind_host = host or self.mind
        if mind_host and hasattr(mind_host, "_snap_to_lattice"):
            try:
                v = mind_host._snap_to_lattice(v, dim or len(v))
            except Exception:
                pass
        return v

    def rerank(self, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """✨ Reranks candidates based on the mind's current primary goal."""
        if not self.mind or not self.mind.goal_field or not self.mind.goal_field.is_initialized or not candidates:
            return candidates

        try:
            top_goal_name, _ = self.mind.goal_field.get_top_goals(k=1)[0]
        except (IndexError, TypeError):
            return candidates

        if top_goal_name == "novelty":
            return self._rerank_for_novelty(candidates)
        elif top_goal_name == "synthesis":
            return self._rerank_for_synthesis(candidates)
        else: # For stability, curiosity, or default
            return self._rerank_for_relevance(candidates)

    def _rerank_for_relevance(self, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Default rerank: boost candidates similar to the current goal vector."""
        goal_vec = self.mind.goal_field.goals[self.mind.goal_field.get_top_goals(k=1)[0][0]]['embedding']
        
        scored = []
        for text, base_score in candidates:
            text_vec = self.mind.memory.main_vectors.get(self.mind.memory.label_to_node_id.get(text))
            if text_vec is None:
                # Fallback for concepts not yet in memory
                text_vec = np.random.rand(len(goal_vec))
                
            similarity = _cosine_similarity(text_vec, goal_vec)
            # Boost score based on relevance to the goal
            final_score = base_score + (similarity * 0.2)
            scored.append((text, final_score))
            
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def _rerank_for_novelty(self, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Boosts candidates that are semantically different from existing memories."""
        scored = []
        for text, base_score in candidates:
            text_vec = self.mind.memory.main_vectors.get(self.mind.memory.label_to_node_id.get(text))
            if text_vec is None:
                scored.append((text, base_score))
                continue

            # Find distance to nearest neighbor in memory
            similar_nodes = self.mind.memory.find_similar_in_main_storage(text_vec, k=1)
            if similar_nodes:
                distance_to_nearest = similar_nodes[0][1]
                # Novelty bonus is proportional to the distance (max bonus of 0.3)
                novelty_bonus = min(0.3, distance_to_nearest * 0.5)
                scored.append((text, base_score + novelty_bonus))
            else:
                scored.append((text, base_score + 0.3)) # Max bonus if no neighbors found
        
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def _rerank_for_synthesis(self, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Boosts candidates that bridge different clusters of concepts in memory."""
        # This is a simplified proxy for finding bridging concepts
        # A full implementation would require community detection on the graph
        return self._rerank_for_relevance(candidates) # Fallback to relevance for now

    # --- Validator persona (deterministic, no emojis) ---
    def validator_persona(self) -> str:
        return "You are a strict scientific validator. Be terse, factual, and output valid JSON only."

    # --- Strip risky Unicode and collapse whitespace (validator-safe) ---
    def sanitize_for_validation(self, text: str) -> str:
        t = (text or "")
        t = unicodedata.normalize("NFKC", t)
        t = t.encode("ascii", "ignore").decode("ascii", "ignore")  # drop emojis/non-ascii
        t = re.sub(r"\s+", " ", t).strip()
        return t[:4000]  # keep prompts small and predictable

    def validator_context_hint(self) -> str:
        if self.mind and getattr(self.mind, "goal_field", None) and self.mind.goal_field.is_initialized:
            try:
                gname, _ = self.mind.goal_field.get_top_goals(k=1)[0]
                return f"[goal={gname}] "
            except Exception:
                pass
        return ""

# The loader will instantiate this.
class _Plugin:
    def __init__(self):
        # This function now returns the class itself, not an instance.
        # The main script will create the instance.
        self.PLUGIN = DynamicScienceSemantics

    def __call__(self):
        return self.PLUGIN

PLUGIN = _Plugin()