import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- Set Page Config ---
st.set_page_config(page_title="NutriVeda", layout="wide", page_icon="🌿")

# --- Custom CSS for Background ---
def set_background_image():
    st.markdown(
        """
        <style>
        /* Set the background image for the entire app */
        .stApp {
            background-image: url("https://img.freepik.com/free-photo/diet-concept-with-female-scientist-healthy-food_23-2148193255.jpg?ga=GA1.1.1149872359.1746710722&semt=ais_hybrid&w=740");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }
        /* Additional styling for text and layout */
        </style>
        """,
        unsafe_allow_html=True
    )

set_background_image()

# --- Custom CSS for layout ---
def apply_custom_css():
    st.markdown(
        """
        <style>
        h1, h2, h3, h4, h5, h6,
        label, .stMarkdown, .stText {
            color: green !important;
        }
        .stSidebar {
            background-color: white !important;
            color: black !important;
            padding-top: 20px;
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div {
            border: 1px solid #00796b !important;
            color: black !important;
            background-color: #ffffff !important;
        }
        .home-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            margin-top: 50px;
        }
        .stButton > button {
            background-color: #00796b;
            color: black;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1.1em;
            margin-bottom: 8px;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #004d40;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_css()

# --- Session State ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'
if 'selected_disease_info' not in st.session_state:
    st.session_state['selected_disease_info'] = None

# --- CSV File Path ---
CSV_FILE_PATH = r"C:\Users\SAKSHI\Desktop\Streamlit\nuitrion data .csv"  # Corrected filename

# --- Load Data ---
@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath, encoding='cp1252')
        df.columns = df.columns.str.strip()
        required_cols = [
            "Disease Name", "Disease Category", "Key Symptoms",
            "Nutritional Considerations", "Foods to Emphasize", "Foods to Limit/Avoid"
        ]
        if not all(c in df.columns for c in required_cols):
            missing = [c for c in required_cols if c not in df.columns]
            st.error(f"Missing columns: {', '.join(missing)}")
            return None
        df['Foods to Emphasize Count'] = df['Foods to Emphasize'].apply(
            lambda x: len([i for i in str(x).split(',') if i.strip()])
        )
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- Navigation functions ---
def navigate_to(page_name):
    st.session_state['page'] = page_name

def navigate_to_home():
    navigate_to('Home')
def navigate_to_about():
    navigate_to('About App')
def navigate_to_about_creator():
    navigate_to('About Creator')
def navigate_to_results(info):
    st.session_state.update({'page': 'Results', 'selected_disease_info': info})
def navigate_to_global_graph():
    navigate_to('Global Graph')
def navigate_to_nutrient_graphs():
    navigate_to('Nutrient Graph')

# --- Plot functions ---

def plot_global_nutrient_count_graph(data):
    st.header("📊 Global Disease vs. Emphasized Item Count")
    counts = data[data['Foods to Emphasize Count'] > 0]
    disease_counts = counts.groupby('Disease Name')['Foods to Emphasize Count'].sum().reset_index()
    if not disease_counts.empty:
        fig, ax = plt.subplots(figsize=(10, max(6, len(disease_counts)*0.4)))
        sns.barplot(x='Foods to Emphasize Count', y='Disease Name', data=disease_counts, palette="viridis", ax=ax)
        ax.set_xlabel('Number of Foods/Nutrients to Emphasize')
        ax.set_ylabel('Disease')
        ax.set_title('Foods/Nutrients to Emphasize Count per Disease')
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("No data to display.")

def plot_disease_nutrient_graphs(data):
    st.header("📈 Disease vs. Emphasized Foods/Nutrients")
    emphasize_data = []
    all_foods = []

    for _, row in data.iterrows():
        disease = row['Disease Name']
        foods = [f.strip() for f in str(row['Foods to Emphasize']).split(',') if f.strip()]
        for food in foods:
            emphasize_data.append({'Disease Name': disease, 'Emphasized Food': food})
            all_foods.append(food)

    if not emphasize_data:
        st.warning("No emphasized food data available.")
        return

    df_emphasize = pd.DataFrame(emphasize_data)
    food_counts = Counter(all_foods)
    top_foods = [food for food, _ in food_counts.most_common(10)]

    for food in top_foods:
        df_food = df_emphasize[df_emphasize['Emphasized Food'] == food]
        if not df_food.empty:
            grouped = df_food.groupby('Disease Name').size().reset_index(name='Count')
            fig, ax = plt.subplots(figsize=(8, max(4, len(grouped)*0.4)))
            sns.barplot(x='Count', y='Disease Name', data=grouped.sort_values('Count', ascending=False), palette="viridis", ax=ax)
            ax.set_title(f"Diseases emphasizing: {food}")
            ax.set_xlabel("Count")
            ax.set_ylabel("Disease")
            st.pyplot(fig)
            plt.close(fig)

# --- Main app logic ---

# Load dataset
data = load_data(CSV_FILE_PATH)

if data is not None:
    # Navigation Buttons
    st.sidebar.header("Navigation")
    if st.sidebar.button("🏠 Home"): navigate_to('Home')
    if st.sidebar.button("ℹ️ About App"): navigate_to('About App')
    if st.sidebar.button("📊 Global Item Count Overview"): navigate_to('Global Graph')
    if st.sidebar.button("📈 Disease vs. Nutrients"): navigate_to('Nutrient Graph')
    if st.sidebar.button("👥 About Creator"): navigate_to('About Creator')

    # Page rendering based on session state
    if st.session_state['page'] == 'Home':
        st.markdown('<div class="home-container">', unsafe_allow_html=True)
        st.header("🌿Nutriveda")
        st.write("Select a disease from the dropdown below.")
        disease_names = data["Disease Name"].dropna().astype(str).unique()
        options = ["Select a disease..."] + sorted(disease_names)
        choice = st.selectbox("Choose a disease:", options, key="disease_select")
        if choice != "Select a disease...":
            info = data[data["Disease Name"] == choice].iloc[0]
            if st.button(f"View Details for {choice}"):
                navigate_to_results(info)
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state['page'] == 'About App':
        st.header("📘 About Nutriveda")
        st.write ("""
        Nutriveda, focused on diseases and their corresponding nutrition, is designed to guide
people in managing or preventing health issues through informed dietary and lifestyle choices.

By offering clear, practical advice, the app empowers users to make smarter food choices.

This app provides information about various diseases and their related nutritional guidance.
It helps you understand what foods are generally considered good and bad for managing certain conditions.

### Global Graphs Explained:

**📊 Global Item Count Overview:**

This bar chart presents a comparative overview of how many foods or nutrients are recommended to be emphasized for various diseases globally. Each bar represents a specific disease, and the length of the bar indicates the total number of dietary items suggested to be emphasized for that disease across the dataset.

**📈 Disease vs. Nutrients:**

This section displays graphs focusing on the **Top 10 Most Emphasized Foods/Nutrients** across all diseases in the dataset. For each of these top nutrients/foods, a bar chart is shown.

Each bar chart shows the diseases that most frequently recommend that specific nutrient/food.

*   The **X-axis** represents the count of times the specific nutrient/food is emphasized for a particular disease.
*   The **Y-axis** lists the diseases that emphasize this nutrient/food.
*   The **bar lengths** indicate how often that nutrient/food is listed under "Foods to Emphasize" for each disease.
*   The title above each graph specifies the nutrient being visualized (e.g., "Diseases Emphasizing: Lean Proteins").

The color gradient in the bars helps visually differentiate the strength of emphasis — the darker the bar, the stronger the association of the nutrient/food with that disease’s dietary recommendations in the dataset.
""")


    elif st.session_state['page'] == 'About Creator':
        st.title("👥 About")
        if st.button("⬅️ Back to Home", key="about_back_home"):
            navigate_to('Home')
        st.markdown("---")
        # About section content
        st.markdown("""
        <div class="about-section-container">
            <h3>👩‍🔬 About the Author</h3>
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="https://media.licdn.com/dms/image/v2/D4D03AQFKK3ZUd4IUfQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1719908816661?e=1752105600&v=beta&t=k7ihdILNcMFCAxP8qZSXCzIA1f5SUte4pFOAxM8LKGs"
                class="profile-image" width="100" height="100">
                <div>
                    <h4>Sakshi Jagtap</h4>
                    <p>M.Sc. Bioinformatics Student at DES Pune University</p>
                    <p>MSc I'm currently pursuing my MSc in Bioinformatics, driven by a deep interest in computational biology, nutrigenomics, and rare disease research. I enjoy exploring how bioinformatics, machine learning, and network analysis can reveal the links between genes, diseases, and nutrition. My focus is on understanding how nutrition impacts various diseases and using data to make those connections clearer. I'm also passionate about making complex biological data more accessible through interactive dashboards—using tools like Power BI, Tableau, Streamlit, and Python/R. Ultimately, I aim to bring together biology and data to support more personalized and nutrition-focused healthcare.</p>
                    <p>🔗 <a href="https://www.linkedin.com/in/sakshi-jagtap-38251a283" target="_blank">Connect on LinkedIn</a></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Mentorship Section
        st.markdown("""
        <div class="about-section-container">
            <h3>👨‍🏫 Mentorship</h3>
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="https://media.licdn.com/dms/image/v2/D5603AQF9gsU7YBjWVg/profile-displayphoto-shrink_400_400/B56ZZI.WrdH0Ag-/0/1744981029051?e=1752105600&v=beta&t=F4QBDSEgjUvnBS00xPkKqPTLI0jQaMpYefaOzARY1Yg"
                class="profile-image" width="100" height="100">
                <div>
                    <h4>Dr. Kushagra Kashyap</h4>
                    <p>Assistant Professor (Bioinformatics), Department of Life Sciences, School of Science and Mathematics, DES Pune University</p>
                    <p>This project was developed under the guidance of Dr. Kashyap, who provided valuable insights and mentorship throughout the development process. His expertise in bioinformatics and computational biology was instrumental in shaping this project.</p>
                    <p>🔗 <a href="https://www.linkedin.com/in/dr-kushagra-kashyap-b230a3bb" target="_blank">Connect on LinkedIn</a></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state['page'] == 'Results':
        st.header("📄 Disease Details")
        if st.button("← Back to Search"):
            navigate_to('Home')
        info = st.session_state.get('selected_disease_info')
        if info is not None:
            # Show disease details
            st.subheader(info['Disease Name'])
            st.write(f"**Category:** {info['Disease Category']}")
            st.write(f"**Key Symptoms:** {info['Key Symptoms']}")
            st.write(f"**Nutritional Considerations:** {info['Nutritional Considerations']}")
            st.write(f"**Foods to Emphasize:** {info['Foods to Emphasize']}")
            st.write(f"**Foods to Limit/Avoid:** {info['Foods to Limit/Avoid']}")
            # Show emphasize count
            emphasize_count = info.get('Foods to Emphasize Count', 0)
            st.markdown(f"### 📊 Foods/Nutrients to Emphasize Count: {emphasize_count}")
            if emphasize_count > 0:
                fig, ax = plt.subplots(figsize=(6, 2))
                sns.barplot(x=[info['Disease Name']], y=[emphasize_count], palette="viridis", ax=ax)
                ax.set_xlabel('Disease')
                ax.set_ylabel('Count')
                ax.set_title('Emphasized Items Count')
                ax.set_ylim(0, emphasize_count * 1.2 + 1)
                ax.set_xticks([])
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No foods/nutrients listed to emphasize for this disease.")
        else:
            st.error("No disease selected.")
            navigate_to('Home')

    elif st.session_state['page'] == 'Global Graph':
        plot_global_nutrient_count_graph(data)

    elif st.session_state['page'] == 'Nutrient Graph':
        plot_disease_nutrient_graphs(data)

else:
    st.error("Failed to load data. Please check the CSV path or format.")