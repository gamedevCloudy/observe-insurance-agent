"""Generate one-pager PDFs for the Observe Insurance knowledge base."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "pdfs"


def build_pdf(filename: str, title: str, sections: list[tuple[str, str]]):
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=20)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=13, spaceAfter=6)
    body_style = ParagraphStyle("Body2", parent=styles["BodyText"], fontSize=11, spaceAfter=10)

    story = [Paragraph(title, title_style)]
    for heading, body in sections:
        story.append(Paragraph(heading, heading_style))
        story.append(Paragraph(body, body_style))
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    print(f"  Created {path.name}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    build_pdf(
        "working_hours.pdf",
        "Observe Insurance — Support Working Hours",
        [
            ("General Support", "Phone and live chat support is available Monday through Friday, 8:00 AM to 6:00 PM Eastern Time. We are closed on New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving, and Christmas Day."),
            ("Claims Hotline", "Our dedicated claims hotline (1-800-555-CLAIM) operates 24 hours a day, 7 days a week, 365 days a year for urgent claim filings."),
            ("Online & Mobile", "You can manage your policy, file claims, and make payments at observeinsurance.com or through our mobile app at any time. Processing of online submissions occurs during business hours."),
            ("Regional Offices", "All five regional offices (Northeast, Southeast, Midwest, Southwest, West) are open to walk-in visitors Monday through Friday, 9:00 AM to 5:00 PM local time. Appointments recommended for complex matters."),
        ],
    )

    build_pdf(
        "mailing_addresses.pdf",
        "Observe Insurance — Mailing Addresses by District",
        [
            ("Northeast District", "Observe Insurance, Northeast Regional Office<br/>200 Park Avenue, Suite 400<br/>New York, NY 10166"),
            ("Southeast District", "Observe Insurance, Southeast Regional Office<br/>3500 Lenox Road, Suite 800<br/>Atlanta, GA 30326"),
            ("Midwest District", "Observe Insurance, Midwest Regional Office<br/>233 South Wacker Drive, Suite 2500<br/>Chicago, IL 60606"),
            ("Southwest District", "Observe Insurance, Southwest Regional Office<br/>500 North Akard Street, Suite 1200<br/>Dallas, TX 75201"),
            ("West District", "Observe Insurance, West Regional Office<br/>555 California Street, Suite 2100<br/>San Francisco, CA 94104"),
            ("Important", "Please include your policy number on all correspondence. Allow 5-7 business days for mail processing. For time-sensitive documents, consider uploading them through your online account."),
        ],
    )

    build_pdf(
        "claim_initiation.pdf",
        "Observe Insurance — How to Start a Claim",
        [
            ("Step 1: Report the Incident", "Contact us as soon as possible after the incident. You can file a claim by calling 1-800-555-CLAIM (available 24/7), visiting observeinsurance.com/claims, using the mobile app, or contacting your assigned agent."),
            ("Step 2: Provide Details", "Have your policy number ready. Describe what happened, when and where the incident occurred, and the extent of the damage or loss. If others were involved, provide their contact and insurance information."),
            ("Step 3: Document Everything", "Take photos or videos of the damage. Keep receipts for any emergency repairs or temporary living expenses. Do not discard damaged items until your adjuster advises you to do so."),
            ("Step 4: Adjuster Assignment", "A claims adjuster will be assigned to your case within 24-48 hours of filing. They will contact you to schedule an inspection and explain the next steps."),
            ("Step 5: Track Your Claim", "Monitor your claim status anytime at observeinsurance.com/my-claims or through the mobile app. Your adjuster will provide updates at each stage of the process."),
        ],
    )

    build_pdf(
        "general_claims_process.pdf",
        "Observe Insurance — General Claims Process",
        [
            ("Overview", "Our claims process is designed to be transparent and efficient. From filing to resolution, you will be kept informed at every step. Standard claims are processed within 10-15 business days."),
            ("Filing", "Once you file a claim, you receive a confirmation email with your claim ID. Use this ID in all future communications. Our system assigns a priority level based on the type and severity of the incident."),
            ("Investigation", "Your assigned adjuster reviews the details, inspects the damage, and may request additional documentation. Cooperating promptly helps speed up the process."),
            ("Evaluation", "The adjuster evaluates your claim against your policy terms and determines the coverage amount. You will receive a detailed explanation of the settlement offer."),
            ("Resolution", "Upon approval, payment is issued within 5-10 business days via your preferred method (direct deposit or check). If you disagree with the settlement, you may appeal within 30 days."),
            ("Expedited Processing", "Diamond and Platinum plan holders have access to expedited claims processing, reducing the standard timeline by up to 50%. Contact your agent or call our priority line for details."),
        ],
    )

    build_pdf(
        "health_insurance_tiers.pdf",
        "Observe Insurance — Health Insurance Plan Tiers",
        [
            ("Bronze Plan", "Most affordable option for basic catastrophic coverage. Deductible: $5,000 individual / $10,000 family. Monthly premium from $180. Out-of-pocket max: $9,000. Covers essential health benefits with higher cost-sharing."),
            ("Silver Plan", "Entry-level tier with balanced coverage. Deductible: $3,000 individual / $6,000 family. Monthly premium from $250. Out-of-pocket max: $7,500. Good for individuals wanting basic coverage at an affordable price."),
            ("Gold Plan", "Comprehensive coverage with moderate deductibles. Deductible: $1,500 individual / $3,000 family. Monthly premium from $400. Out-of-pocket max: $5,000. Our most popular plan for families. Includes expanded specialist and mental health access."),
            ("Diamond Plan", "Premium coverage with low deductibles. Deductible: $500 individual / $1,000 family. Monthly premium from $600. Out-of-pocket max: $3,000. Includes dental, vision, and chiropractic care."),
            ("Platinum Plan", "Top-tier offering with the lowest out-of-pocket costs. Deductible: $0. Monthly premium from $900. Out-of-pocket max: $1,500. Includes concierge health services, international coverage, and wellness programs."),
            ("Choosing Your Plan", "Consider your typical healthcare usage, budget, and preferred providers. Bronze suits healthy individuals wanting catastrophic protection. Gold and Diamond offer the best balance for families. Platinum is ideal for those who want comprehensive coverage with minimal out-of-pocket expenses."),
        ],
    )


if __name__ == "__main__":
    main()
