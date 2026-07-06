def test_save_and_retrieve_evaluation(in_memory_db):
    record = in_memory_db.save_evaluation(
        topic="Photosynthesis",
        transcript="Plants convert light into energy.",
        semantic_score=88.0,
        fluency_score=75.0,
        overall_score=82.8,
        grade="Excellent",
        feedback="Great job!",
        words_per_minute=140.0,
        filler_count=2,
        pause_count=3,
        report_path="/tmp/fake_report.pdf",
    )

    assert record.id is not None

    all_records = in_memory_db.get_all_evaluations()
    assert len(all_records) == 1
    assert all_records[0].topic == "Photosynthesis"
    assert all_records[0].overall_score == 82.8


def test_filter_by_topic(in_memory_db):
    in_memory_db.save_evaluation(
        topic="TCP vs UDP", transcript="...", semantic_score=70, fluency_score=70,
        overall_score=70, grade="Good", feedback="ok",
    )
    in_memory_db.save_evaluation(
        topic="The Water Cycle", transcript="...", semantic_score=60, fluency_score=60,
        overall_score=60, grade="Fair", feedback="ok",
    )

    tcp_only = in_memory_db.get_evaluations_by_topic("TCP vs UDP")
    assert len(tcp_only) == 1
    assert tcp_only[0].topic == "TCP vs UDP"


def test_to_dict_serialization(in_memory_db):
    record = in_memory_db.save_evaluation(
        topic="Newton's Second Law of Motion", transcript="F=ma", semantic_score=95,
        fluency_score=90, overall_score=93, grade="Excellent", feedback="Nice work",
    )
    d = record.to_dict()
    assert d["topic"] == "Newton's Second Law of Motion"
    assert d["overall_score"] == 93
    assert "created_at" in d
