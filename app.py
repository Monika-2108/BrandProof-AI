import streamlit as st
import json

from database.db import (
    get_verification_history,
    save_verification
)

from modules.brand_knowledge import (
    create_brand_profile,
    get_brand_profile
)

from modules.content_checker import check_brand_content

from modules.approval import (
    submit_for_approval,
    review_content,
    get_latest_approval
)

from modules.publish_passport import (
    create_publish_passport,
    get_all_passports,
    verify_passport
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="BrandProof | Brand Intelligence",
    page_icon="ðŸ›¡ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM DESIGN SYSTEM
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --background: #080B09;
    --sidebar: #101712;
    --surface: #141C16;
    --surface-hover: #19251C;
    --green: #166534;
    --green-light: #22C55E;
    --green-soft: #173D25;
    --white: #F5F7F5;
    --muted: #A3ADA5;
    --border: #26352A;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--background);
    color: var(--white);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: var(--sidebar);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--muted) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--muted) !important;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--white) !important;
}

p, li, label {
    color: var(--muted);
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 22px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
}

div[data-testid="stMetricValue"] {
    color: var(--white) !important;
    font-family: 'Space Grotesk', sans-serif;
}

.stButton > button {
    background: var(--green);
    color: white;
    border: 1px solid #267C43;
    border-radius: 9px;
    min-height: 43px;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #1B7A3C;
    border-color: var(--green-light);
    color: white;
}

.stButton > button:focus {
    color: white;
    border-color: var(--green-light);
}

button[kind="primary"] {
    background: var(--green) !important;
    border-color: var(--green-light) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #101712 !important;
    color: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #101712;
    border-color: var(--border);
    color: var(--white);
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label {
    color: var(--white) !important;
}

div[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}

div[data-testid="stExpander"] summary {
    color: var(--white);
}

hr {
    border-color: var(--border);
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

.brand-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 27px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -1px;
}

.brand-logo span {
    color: #22C55E;
}

.brand-tagline {
    font-size: 11px;
    color: #8F9B92;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
}

.hero {
    background: linear-gradient(115deg, #14291A, #101712 65%, #101D14);
    border: 1px solid #285235;
    border-radius: 18px;
    padding: 34px;
    margin-bottom: 25px;
}

.hero-label {
    color: #72D98C;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 34px;
    font-weight: 700;
    margin-top: 12px;
    line-height: 1.25;
}

.hero-description {
    color: #B1C1B5;
    font-size: 15px;
    margin-top: 12px;
    max-width: 650px;
    line-height: 1.7;
}

.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: #FFFFFF;
    margin-top: 25px;
    margin-bottom: 15px;
}

.feature-card {
    background: #141C16;
    border: 1px solid #26352A;
    border-radius: 14px;
    padding: 22px;
    min-height: 145px;
}

.feature-icon {
    font-size: 23px;
    margin-bottom: 12px;
}

.feature-title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
}

.feature-description {
    color: #9BA99F;
    font-size: 12px;
    margin-top: 8px;
    line-height: 1.6;
}

.status-approved {
    color: #4ADE80;
    font-weight: 700;
}

.status-review {
    color: #FBBF24;
    font-weight: 700;
}

.small-caption {
    color: #8F9B92;
    font-size: 12px;
}

.passport-card {
    background: linear-gradient(135deg, #14291A, #101712);
    border: 1px solid #357A46;
    border-radius: 16px;
    padding: 25px;
}

.passport-code {
    color: #4ADE80;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 23px;
    font-weight: 700;
    letter-spacing: 2px;
}

[data-testid="stProgressBar"] > div > div {
    background-color: #22C55E;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# APPLICATION DATA
# --------------------------------------------------

profile = get_brand_profile()
history = get_verification_history()
passports = get_all_passports()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("""
    <div class="brand-logo">Brand<span>Proof</span></div>
    <div class="brand-tagline">Brand Intelligence Platform</div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Brand Guidelines",
            "Content Verification",
            "Human Approval",
            "Publish Passport",
            "Verification History"
        ],
        label_visibility="visible"
    )

    st.markdown("---")

    st.markdown("**WORKSPACE STATUS**")

    if profile:
        st.markdown(
            f"<p class='status-approved'>â— Brand Active</p>",
            unsafe_allow_html=True
        )
        st.caption(profile["brand_name"])
    else:
        st.markdown(
            "<p style='color:#FBBF24'>â— Setup Required</p>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        "<p class='small-caption'>BRANDPROOF v1.0</p>",
        unsafe_allow_html=True
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <div class="hero-label">BRAND INTELLIGENCE / OVERVIEW</div>
        <div class="hero-title">
            Trust Before You Publish.
        </div>
        <div class="hero-description">
            One intelligent platform to protect brand identity,
            verify content compliance and establish publishing trust.
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = len(history)

    approved = sum(
        1 for item in history
        if item["status"] == "Approved"
    )

    needs_review = sum(
        1 for item in history
        if item["status"] == "Needs Review"
    )

    pending = sum(
        1 for item in history
        if (
            get_latest_approval(item["id"]) is None
            or get_latest_approval(item["id"])["decision"] == "Pending"
        )
    )

    st.markdown(
        '<div class="section-heading">Platform Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Verifications", total)
    col2.metric("Passed Rule Checks", approved)
    col3.metric("Needs Review", needs_review)
    col4.metric("Publish Passports", len(passports))

    st.markdown(
        '<div class="section-heading">Your Workspace</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">◆</div>
            <div class="feature-title">Brand Knowledge</div>
            <div class="feature-description">
                Centralize your brand identity, communication tone
                and compliance requirements.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Content Intelligence</div>
            <div class="feature-description">
                Detect guideline violations and measure
                content compliance.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✦</div>
            <div class="feature-title">Publishing Trust</div>
            <div class="feature-description">
                Review content and issue cryptographic
                Publish Passports.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Recent Activity</div>',
        unsafe_allow_html=True
    )

    if not history:
        st.info("No activity yet. Start by verifying your first content.")
    else:

        for item in history[:5]:

            approval = get_latest_approval(item["id"])

            approval_status = (
                approval["decision"]
                if approval else "Pending"
            )

            with st.container(border=True):

                col1, col2, col3 = st.columns([3, 2, 2])

                col1.markdown(
                    f"**Verification #{item['id']}**"
                )

                col1.caption(item["brand_name"])

                col2.write(item["status"])

                col3.caption(
                    f"Human review: {approval_status}"
                )


# --------------------------------------------------
# BRAND GUIDELINES
# --------------------------------------------------

elif page == "Brand Guidelines":

    st.title("Brand Knowledge")
    st.caption("Define and manage your organization's brand identity.")

    existing = profile or {}

    tones = [
        "Professional",
        "Friendly",
        "Formal",
        "Innovative",
        "Casual",
        "Trustworthy"
    ]

    with st.form("brand_form"):

        st.subheader("Brand Identity")

        brand_name = st.text_input(
            "Organization / Brand Name",
            value=existing.get("brand_name", "")
        )

        tone = st.selectbox(
            "Communication Tone",
            tones,
            index=(
                tones.index(existing["tone"])
                if existing.get("tone") in tones
                else 0
            )
        )

        st.divider()

        st.subheader("Compliance Rules")

        forbidden = st.text_area(
            "Restricted Words and Phrases",
            value=", ".join(existing.get("forbidden_words", [])),
            placeholder="cheap, fake, guaranteed"
        )

        required = st.text_area(
            "Mandatory Words and Phrases",
            value=", ".join(existing.get("required_words", [])),
            placeholder="official, trusted, quality"
        )

        max_length = st.number_input(
            "Maximum Word Count",
            min_value=50,
            max_value=10000,
            value=int(existing.get("max_length", 500))
        )

        submitted = st.form_submit_button(
            "Save Brand Configuration",
            use_container_width=True
        )

        if submitted:

            if not brand_name.strip():
                st.error("Brand name is required.")

            else:

                create_brand_profile(
                    brand_name,
                    tone,
                    forbidden,
                    required,
                    max_length
                )

                st.success("Brand configuration saved.")
                st.rerun()

    if profile:

        st.divider()

        st.subheader("Active Brand Configuration")

        a, b = st.columns(2)

        with a:
            st.write("**Brand:**", profile["brand_name"])
            st.write("**Tone:**", profile["tone"])

        with b:
            st.write("**Maximum words:**", profile["max_length"])
            st.write("**Restricted phrases:**",
                     len(profile["forbidden_words"]))


# --------------------------------------------------
# CONTENT VERIFICATION
# --------------------------------------------------

elif page == "Content Verification":

    st.title("Content Intelligence")
    st.caption("Analyze marketing content against your brand rules.")

    if not profile:

        st.warning("Create a brand profile before starting verification.")

    else:

        st.markdown(
            f"**Active brand:** {profile['brand_name']}"
        )

        content_type = st.selectbox(
            "Select Content Category",
            [
                "Social Media Post",
                "Advertisement",
                "Marketing Email",
                "Website Content",
                "Product Description",
                "Other"
            ]
        )

        content = st.text_area(
            "Content to Verify",
            height=250,
            placeholder="Paste your marketing content here..."
        )

        if st.button(
            "Analyze Content",
            type="primary",
            use_container_width=True
        ):

            if not content.strip():

                st.error("Please enter content to analyze.")

            else:

                result = check_brand_content(
                    content,
                    profile
                )

                verification_id = save_verification(
                    profile["brand_name"],
                    content,
                    result["status"],
                    json.dumps(result["violations"])
                )

                submit_for_approval(
                    verification_id,
                    "BrandProof Review System",
                    f"Content category: {content_type}"
                )

                st.session_state["last_result"] = result
                st.session_state["last_verification_id"] = verification_id
                st.session_state["last_content"] = content

                st.rerun()

        if "last_result" in st.session_state:

            result = st.session_state["last_result"]

            st.divider()

            st.subheader("Verification Report")

            a, b, c = st.columns(3)

            a.metric(
                "Compliance Score",
                f"{result['score']}%"
            )

            b.metric(
                "Word Count",
                result["word_count"]
            )

            c.metric(
                "Detected Issues",
                len(result["violations"])
            )

            st.progress(result["score"] / 100)

            if result["status"] == "Approved":
                st.success("All configured rule checks passed.")
            else:
                st.warning("Content requires further review.")

            st.subheader("Detected Violations")

            if result["violations"]:

                for issue in result["violations"]:
                    st.error(issue)

            else:
                st.success("No configured rule violations detected.")

            st.subheader("Additional Warnings")

            if result["warnings"]:

                for warning in result["warnings"]:
                    st.warning(warning)

            else:
                st.info("No additional warnings.")

            st.subheader("Correction Suggestions")

            for suggestion in result["suggestions"]:
                st.write("â€¢", suggestion)

            st.caption(
                f"Verification ID: "
                f"{st.session_state['last_verification_id']}"
            )

            st.caption(
                "Automated checks are rule-based. Human review is "
                "required before a Publish Passport can be issued."
            )


# --------------------------------------------------
# HUMAN APPROVAL
# --------------------------------------------------

elif page == "Human Approval":

    st.title("Human Approval Center")

    st.caption(
        "The final human decision before content receives publishing authorization."
    )

    if not history:

        st.info("No verification records available.")

    else:

        pending_items = []

        for item in history:

            approval = get_latest_approval(item["id"])

            if not approval or approval["decision"] == "Pending":
                pending_items.append(item)

        st.metric("Awaiting Final Decision", len(pending_items))

        if not pending_items:
            st.success("All submitted records have been reviewed.")

        for item in pending_items:

            with st.expander(
                f"Verification #{item['id']} | {item['brand_name']}"
            ):

                st.markdown("**Submitted Content**")
                st.write(item["content"])

                st.write(
                    "**Automated Status:**",
                    item["status"]
                )

                reviewer = st.text_input(
                    "Reviewer Name",
                    key=f"reviewer_{item['id']}"
                )

                comments = st.text_area(
                    "Review Comments",
                    key=f"comments_{item['id']}"
                )

                left, right = st.columns(2)

                with left:

                    if st.button(
                        "Approve Content",
                        key=f"approve_{item['id']}"
                    ):

                        if not reviewer.strip():
                            st.error("Enter reviewer name.")

                        else:

                            success, message = review_content(
                                item["id"],
                                "Approved",
                                reviewer,
                                comments
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                with right:

                    if st.button(
                        "Reject Content",
                        key=f"reject_{item['id']}"
                    ):

                        if not reviewer.strip():
                            st.error("Enter reviewer name.")

                        else:

                            success, message = review_content(
                                item["id"],
                                "Rejected",
                                reviewer,
                                comments
                            )

                            if success:
                                st.warning(message)
                                st.rerun()
                            else:
                                st.error(message)


# --------------------------------------------------
# PUBLISH PASSPORT
# --------------------------------------------------

elif page == "Publish Passport":

    st.title("Publish Passport")

    st.caption(
        "A digital proof of human approval and content integrity."
    )

    approved_items = []

    for item in history:

        approval = get_latest_approval(item["id"])

        if approval and approval["decision"] == "Approved":
            approved_items.append(item)

    if approved_items:

        selected = st.selectbox(
            "Select Human-Approved Content",
            approved_items,
            format_func=lambda x: (
                f"Verification #{x['id']} | {x['brand_name']}"
            )
        )

        if st.button(
            "Generate Publish Passport",
            type="primary",
            use_container_width=True
        ):

            passport, message = create_publish_passport(
                selected["id"]
            )

            if passport:

                st.session_state["generated_passport"] = passport
                st.success(message)

            else:
                st.error(message)

    else:

        st.info(
            "No human-approved content is available for passport generation."
        )

    if "generated_passport" in st.session_state:

        passport = st.session_state["generated_passport"]

        st.divider()

        st.subheader("Digital Publish Passport")

        st.markdown("""
        <div class="passport-card">
            <div class="hero-label">BRANDPROOF / VERIFIED RECORD</div>
            <br>
            <div style="color:#FFFFFF;font-size:22px;font-weight:700;">
                Publishing Trust Certificate
            </div>
            <br>
            <div style="color:#A3ADA5;font-size:12px;">
                UNIQUE PASSPORT IDENTIFIER
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<div class='passport-code'>{passport['passport_code']}</div>",
            unsafe_allow_html=True
        )

        st.write("**Brand:**", passport["brand_name"])
        st.write("**Verification ID:**", passport["verification_id"])
        st.write("**SHA-256 Content Hash:**")

        st.code(passport["content_hash"])

        st.write("**Issued At:**", passport["issued_at"])

        st.download_button(
            "Download Passport JSON",
            data=json.dumps(passport, indent=4),
            file_name=f"{passport['passport_code']}.json",
            mime="application/json"
        )

    st.divider()

    st.subheader("Verify a Passport")

    passport_code = st.text_input(
        "Enter Passport Identifier",
        placeholder="BP-XXXXXXXXXXXX"
    )

    if st.button("Verify Authenticity"):

        if passport_code.strip():

            result = verify_passport(passport_code.strip())

            if result["valid"]:
                st.success(result["message"])
                passport_data = result["passport"]

                with st.container(border=True):
                    st.markdown("### 🛡️ Passport Verification Certificate")
                    st.caption("BRANDPROOF / AUTHENTICITY RECORD")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Passport Identifier**")
                        st.code(passport_data["passport_code"], language=None)

                        st.markdown("**Brand Name**")
                        st.write(passport_data["brand_name"])

                    with col2:
                        st.markdown("**Verification ID**")
                        st.write(f'#{passport_data["verification_id"]}')

                        st.markdown("**Status**")
                        st.success("Authentic")

                    st.divider()

                    st.markdown("**SHA-256 Content Hash**")
                    st.code(passport_data["content_hash"], language=None)

                    st.markdown("**Issued At**")
                    st.write(passport_data["issued_at"])
            else:
                st.error(result["message"])

        else:
            st.warning("Enter a passport identifier.")

    st.divider()

    st.subheader("Previously Issued Passports")

    if passports:

        for passport in passports:

            with st.expander(passport["passport_code"]):

                st.write("**Brand:**", passport["brand_name"])
                st.write("**Verification ID:**",
                         passport["verification_id"])
                st.write("**Issued:**", passport["issued_at"])

    else:
        st.caption("No passports have been issued yet.")


# --------------------------------------------------
# VERIFICATION HISTORY
# --------------------------------------------------

elif page == "Verification History":

    st.title("Verification Records")

    st.caption(
        "A complete record of submitted content and review decisions."
    )

    if not history:

        st.info("Your verification history is currently empty.")

    else:

        search = st.text_input(
            "Search by brand name or content"
        )

        for item in history:

            searchable = (
                item["brand_name"] + " " + item["content"]
            ).lower()

            if search.lower() not in searchable:
                continue

            approval = get_latest_approval(item["id"])

            with st.expander(
                f"#{item['id']} | {item['brand_name']} | {item['status']}"
            ):

                st.markdown("**Content**")
                st.write(item["content"])

                st.write("**Automated Decision:**", item["status"])

                st.write(
                    "**Human Decision:**",
                    approval["decision"] if approval else "Pending"
                )

                st.write("**Created:**", item["created_at"])

                if item["violations"]:

                    st.markdown("**Detected Violations**")

                    try:
                        violations = json.loads(item["violations"])

                        for violation in violations:
                            st.warning(violation)

                    except json.JSONDecodeError:
                        st.write(item["violations"])


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.markdown("---")

st.sidebar.markdown(
    "<p style='color:#718078;font-size:11px;'>"
    "Â© 2026 BrandProof AI<br>"
    "Trust Before You Publish."
    "</p>",
    unsafe_allow_html=True
)

