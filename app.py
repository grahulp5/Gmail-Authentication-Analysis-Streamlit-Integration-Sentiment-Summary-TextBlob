import streamlit as st
import streamlit.components.v1 as stc
from RetrieveSpam import analysis
from SentimentAnalysis import sentanalysis

# HTML template for the header
html_temp = """
    <div style="background-color:#F05A22;padding:10px;border-radius:10px">
    <h1 style="color:black;text-align:center;font-family:Roboto, sans-serif;">📧 Gmail Analysis Web App</h1>
    </div>
    """

# Custom CSS for fonts and emojis
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    .emoji {
        font-size: 1.5em;
    }
    .header-home {
        font-size: 2.5em;
        font-weight: bold;
    }
    .header-large {
        font-size: 2em;
        font-weight: bold;
        #text-align: center;
    }
    .subheader {
        font-size: 1.5em;
        font-weight: bold;
        #text-align: center;
    }
    .paragraph {
        font-size: 1.2em;
        #text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    stc.html(html_temp)
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio('Go to', ['Home', 'Word cloud', 'Sentiment Analysis'])

    if choice == "Home":
        st.markdown("<div class='header-home'>Home</div>", unsafe_allow_html=True)
        st.markdown("""
                    <div class='subheader'>Lets Retrieve Emails and do some Analysis</div>
                    <p></p><p class='paragraph'>This application is used to connect your Gmail account and get information.</p> 
                    <p>Go to ▶️ Navigation tab and do either word cloud of common words from your gmail spam's folder,
                    or summarise and check sentiments for 1 of your emails from the latest 30 emails.</p>
                    <p></p>
                    <p>Don't forget to delete ❌ "token.pickle" file to change the gmail being used.</p>
                """, unsafe_allow_html=True)

    elif choice == "Word cloud":
        st.markdown("<div class='header-home'>☁️ Word Cloud from Spam Folder in Gmail</div>", unsafe_allow_html=True)
        st.markdown("""
                            <div class='subheader'>The word cloud snapshot</div>
                            <p></p><p class='paragraph'>Here is the snapshot for the most common 50 words
                            from your spam folder. </p>
                            <p>This is also saved in your folder.</p>
                        """, unsafe_allow_html=True)
        analysis()

    elif choice == "Sentiment Analysis":
        st.markdown("<div class='header-home'>😊😐😢 Gmail Analysis</div>", unsafe_allow_html=True)
        st.markdown("""
                                    <div class='subheader'>Summary and Sentiment Analysis</div>
                                    <p></p><p class='paragraph'>Here we select one email from your latest 30 emails from all mail,
                                     and then we do sentiment analysis and summary for that email.</p>
                                    
                                """, unsafe_allow_html=True)
        sentanalysis()

if __name__ == '__main__':
    main()

#RahulGupta
#https://www.linkedin.com/in/rahul-gupta-a31749166/