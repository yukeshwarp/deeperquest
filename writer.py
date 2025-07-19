from config import client
import logging


def report_writer(context):
    """Generates a highly detailed research report from completed steps and results, with full source attribution and comprehensive coverage."""
    report_prompt = (
        f"Given the following completed research steps and their results:\n{context}\n\n"
        "As an autonomous research agent, write a highly detailed, exhaustive, and well-structured research report that answers the original query. "
        "Include attribution to all sources referenced or used in any step. "
        "Ensure that every piece of information, even if only slightly related to the research topic, is included and clearly explained. "
        "Organize the report with clear sections, provide in-depth analysis, and cite all sources explicitly. "
        "If possible, include a bibliography or references section at the end listing all sources."
        "Also mention the numerical count of total number of resources used in the report, including web pages, papers, and articles."
    )
    report_response = client.chat.completions.create(
        model="model-router",
        messages=[
            {
                "role": "system",
                "content": "You are a research report writing assistant.",
            },
            {"role": "user", "content": report_prompt},
        ],
    )
    model_name = getattr(report_response, 'model', None)
    if model_name:
        logging.info(f"Report generated using model: {model_name}")
    return report_response.choices[0].message.content


def eval_agent(context, research_target, max_attempts=3):
    """Evaluates if the generated report meets the research target. If not, reruns report_writer up to 3 times."""
    for attempt in range(1, max_attempts + 1):
        report = report_writer(context)
        eval_prompt = (
            f"Research Target: {research_target}\n\n"
            f"Generated Report:\n{report}\n\n"
            "As an evaluation agent, assess if the report fully and satisfactorily meets the research target. "
            "Reply with 'YES' if it does, or 'NO' if it does not. If 'NO', briefly state what is missing or could be improved."
        )
        eval_response = client.chat.completions.create(
            model="model-router",
            messages=[
                {"role": "system", "content": "You are a critical research report evaluator."},
                {"role": "user", "content": eval_prompt},
            ],
        )
        model_name = getattr(eval_response, 'model', None)
        if model_name:
            logging.info(f"Eval agent used model: {model_name}")
        feedback = eval_response.choices[0].message.content.strip().upper()
        if feedback.startswith("YES"):
            return report
        # Optionally, you could use feedback to improve the next report generation
    return report

# Feedback loop