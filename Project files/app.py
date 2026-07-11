"""
VBCUA — Voice-Based Concept Understanding Analyser
Streamlit UI entry point.

Run with:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

import config
from data.topics import get_reference_explanation, get_topic_names
from src import audio_analysis, database, feedback, pdf_report, scoring, semantic_analysis, transcription

st.set_page_config(page_title="VBCUA", page_icon="🎙️", layout="wide")
database.init_db()


def _save_uploaded_file(uploaded_file) -> str:
    dest = config.UPLOAD_DIR / uploaded_file.name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)


def render_analyzer_tab():
    st.subheader("Analyze a Spoken Explanation")

    col1, col2 = st.columns([1, 1])
    with col1:
        topic = st.selectbox("Select a topic", get_topic_names())
        with st.expander("Show reference explanation"):
            st.write(get_reference_explanation(topic))

    with col2:
        audio_file = st.file_uploader(
            "Upload your spoken explanation (wav / mp3 / m4a)",
            type=["wav", "mp3", "m4a"],
        )

    run = st.button("Analyze", type="primary", disabled=audio_file is None)

    if run and audio_file is not None:
        audio_path = _save_uploaded_file(audio_file)

        with st.spinner("Transcribing speech with Whisper..."):
            transcript_result = transcription.transcribe_audio(audio_path)
            transcript_text = transcript_result.text

        st.markdown("#### Transcript")
        st.write(transcript_text or "_No speech detected._")

        with st.spinner("Scoring semantic understanding..."):
            reference = get_reference_explanation(topic)
            semantic_result = semantic_analysis.compute_semantic_score(transcript_text, reference)

        with st.spinner("Analyzing fluency (pauses, fillers, pace)..."):
            fluency_result = audio_analysis.analyze_fluency(audio_path, transcript_text)
            waveform_path = audio_analysis.generate_waveform_image(audio_path)

        overall = scoring.compute_overall_score(semantic_result["score"], fluency_result.fluency_score)

        with st.spinner("Generating AI feedback..."):
            feedback_text = feedback.generate_feedback(
                topic, transcript_text, reference, semantic_result["score"], fluency_result.fluency_score
            )

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Semantic Score", f"{overall.semantic_score:.1f}")
        m2.metric("Fluency Score", f"{overall.fluency_score:.1f}")
        m3.metric("Overall Score", f"{overall.overall_score:.1f}")
        m4.metric("Grade", overall.grade)

        st.markdown("#### Waveform")
        st.image(waveform_path, use_container_width=True)

        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Duration (s)", fluency_result.duration_seconds)
        fc2.metric("Speaking rate (wpm)", fluency_result.words_per_minute)
        fc3.metric("Filler words", fluency_result.filler_count)
        fc4.metric("Pauses (long)", f"{fluency_result.pauses.count} ({fluency_result.pauses.long_pause_count})")

        st.markdown("#### AI Feedback")
        st.info(feedback_text)

        fluency_stats = {
            "duration_seconds": fluency_result.duration_seconds,
            "words_per_minute": fluency_result.words_per_minute,
            "filler_count": fluency_result.filler_count,
            "pauses": {
                "count": fluency_result.pauses.count,
                "long_pause_count": fluency_result.pauses.long_pause_count,
                "total_pause_duration": fluency_result.pauses.total_pause_duration,
            },
        }

        report_path = pdf_report.generate_report(
            topic=topic,
            transcript=transcript_text,
            semantic_score=overall.semantic_score,
            fluency_score=overall.fluency_score,
            overall_score=overall.overall_score,
            grade=overall.grade,
            feedback=feedback_text,
            fluency_stats=fluency_stats,
            waveform_image_path=waveform_path,
        )

        database.save_evaluation(
            topic=topic,
            transcript=transcript_text,
            semantic_score=overall.semantic_score,
            fluency_score=overall.fluency_score,
            overall_score=overall.overall_score,
            grade=overall.grade,
            feedback=feedback_text,
            words_per_minute=fluency_result.words_per_minute,
            filler_count=fluency_result.filler_count,
            pause_count=fluency_result.pauses.count,
            report_path=report_path,
        )

        with open(report_path, "rb") as f:
            st.download_button(
                "Download PDF Report",
                data=f.read(),
                file_name=Path(report_path).name,
                mime="application/pdf",
                type="primary",
            )

        st.success("Evaluation complete and saved to your dashboard.")


def render_dashboard_tab():
    st.subheader("Evaluation Dashboard")
    records = database.get_all_evaluations()

    if not records:
        st.info("No evaluations yet — run an analysis in the first tab to see results here.")
        return

    rows = [
        {
            "Date": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            "Topic": r.topic,
            "Semantic": r.semantic_score,
            "Fluency": r.fluency_score,
            "Overall": r.overall_score,
            "Grade": r.grade,
            "WPM": r.words_per_minute,
            "Fillers": r.filler_count,
        }
        for r in records
    ]

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.markdown("#### Trend: Overall Score Over Time")
    if len(df) > 1:
        st.line_chart(df.set_index("Date")["Overall"])

    st.markdown("#### Download a past report")
    options = {f"#{r.id} — {r.topic} ({r.created_at.strftime('%Y-%m-%d %H:%M')})": r.report_path for r in records}
    choice = st.selectbox("Select an evaluation", list(options.keys()))
    report_path = options[choice]
    if report_path and Path(report_path).exists():
        with open(report_path, "rb") as f:
            st.download_button("Download PDF Report", data=f.read(), file_name=Path(report_path).name, mime="application/pdf")
    else:
        st.warning("Report file not found on disk for this record.")


def main():
    st.title("🎙️ VBCUA — Voice-Based Concept Understanding Analyser")
    st.caption("Evaluate spoken conceptual explanations for both understanding and delivery.")

    tab1, tab2 = st.tabs(["Analyzer", "Dashboard"])
    with tab1:
        render_analyzer_tab()
    with tab2:
        render_dashboard_tab()


if __name__ == "__main__":
    main()
