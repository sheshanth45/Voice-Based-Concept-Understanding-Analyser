"""
Sample topics with reference ("model") explanations that user recordings are
compared against for semantic similarity scoring.

In a production system these would live in the database and be editable by an
instructor, but a static module is enough to make the pipeline fully runnable
out of the box.
"""

TOPICS = {
    "Photosynthesis": (
        "Photosynthesis is the process by which green plants, algae, and some "
        "bacteria convert light energy, usually from the sun, into chemical "
        "energy stored in glucose. It takes place mainly in the chloroplasts, "
        "using carbon dioxide and water as raw materials, and releases oxygen "
        "as a byproduct. The process has two main stages: the light-dependent "
        "reactions, which capture solar energy, and the light-independent "
        "reactions (Calvin cycle), which use that energy to build sugars."
    ),
    "Newton's Second Law of Motion": (
        "Newton's second law states that the acceleration of an object is "
        "directly proportional to the net force acting on it and inversely "
        "proportional to its mass, expressed as F equals m times a. This means "
        "a larger force produces a larger acceleration, while a larger mass "
        "resists acceleration more. The law explains how the motion of "
        "everyday objects changes when forces are applied to them."
    ),
    "Supervised vs Unsupervised Learning": (
        "Supervised learning trains a model on labeled data, where each input "
        "example is paired with the correct output, so the model learns to "
        "map inputs to outputs and can predict labels for new data. "
        "Unsupervised learning, in contrast, works with unlabeled data and "
        "tries to find hidden patterns or structure, such as clusters or "
        "lower-dimensional representations, without being told the correct "
        "answer in advance."
    ),
    "The Water Cycle": (
        "The water cycle describes the continuous movement of water on, "
        "above, and below the surface of the Earth. Water evaporates from "
        "oceans and lakes into the atmosphere, condenses into clouds, falls "
        "back to the surface as precipitation, and eventually flows back into "
        "bodies of water or infiltrates the ground, completing the cycle. "
        "This process is driven by solar energy and gravity."
    ),
    "TCP vs UDP": (
        "TCP is a connection-oriented protocol that guarantees reliable, "
        "ordered delivery of data by establishing a handshake, acknowledging "
        "received packets, and retransmitting lost ones, which makes it "
        "suitable for applications like web browsing and file transfer. UDP "
        "is a connectionless protocol that sends packets without guarantees "
        "of delivery or order, trading reliability for lower latency, which "
        "makes it suitable for real-time applications like video calls and "
        "online gaming."
    ),
}


def get_topic_names():
    """Return the list of available topic titles."""
    return list(TOPICS.keys())


def get_reference_explanation(topic_name: str) -> str:
    """Return the reference explanation text for a given topic."""
    return TOPICS.get(topic_name, "")
