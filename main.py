import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import cv2
from PIL import Image
import sqlite3
from streamlit_lottie import st_lottie
import requests
import face_recognition
import datetime
import matplotlib.pyplot as plt
import os

applicationKey = "8aec4d96-08f3-495d-b923-ecceb72c9a08"
applicationSecret = "rA/s3FGsukSrQvGm/HiMxw=="


conn = sqlite3.connect('database.db')
c = conn.cursor()

parties = ['BJP', 'INC', 'AAP', 'NOTA']

aadar =  [484878748723,783473478233,438877847834,894878754784,894587478434,894887875487,347878487443,848845883388,237837887487,894589488453,484774775443,848784587443,484785788454,848488745833,945988958453,845884588787,894588458845,458989548845,945998589895]
voteid = [834643734676,755674377643,347747457472,437787834873,783878738734,347878348778,757464674743,348792982878,648457457745,834484587785,589458845894,484878484584,458949984984,589459904444,348983474434,845887544744,348893487843,458989458484,984589854854]

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT, email TEXT,DOB TEXT,Gender TEXT,area TEXT,Aadr TEXT, voterid TEXT, mobilenumber TEXT, time TEXT)')

def add_userdata(username,password,email,dob,gender,area,aadr,voterid,mobilenumber, time):
	c.execute('INSERT INTO userstable(username,password,email,dob,gender,area,aadr,voterid,mobilenumber,time) VALUES (?,?,?,?,?,?,?,?,?,?)',(username,password,email,dob,gender,area,aadr,voterid,mobilenumber, time))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def animation(value):
    r = requests.get(value)
    if r.status_code != 200:
        return None
    return r.json()

def plot(val):
    st_lottie(
            val,
            speed=1,
            reverse=False,
            loop=True,
            quality="High",
            #renderer="svg",
            height=400,
            width=-900,
            key=None,
        )


def vote_table():
    c.execute('CREATE TABLE IF NOT EXISTS votetable(username TEXT,party TEXT, password TEXT)')

def add_vote(username,party,password):
    c.execute('INSERT INTO votetable(username,party,password) VALUES (?,?,?)',(username,party,password))
    conn.commit()

def get_votes(party):
    c.execute('SELECT * FROM votetable WHERE party = ?',(party,))
    data = c.fetchall()
    return data

def get_mobilenumber(username,password):
    c.execute('SELECT mobilenumber FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def get_time(username,password):
    c.execute('SELECT time FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

def check_vote(username,password):
    c.execute('SELECT party FROM votetable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

def check_user(aadr,voterid):
    c.execute('SELECT * FROM userstable WHERE aadr =? AND voterid = ?',(aadr,voterid))
    data = c.fetchall()
    return data

def main():
    st.title("Smart Voting System using Facial Recognition")
    menu = ["AdminPage", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)
    anim = animation('https://assets7.lottiefiles.com/packages/lf20_MtN0BG.json')
    plot(anim)

    if choice == "AdminPage":
        st.subheader("Admin Page")
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            if username == 'admin' and password == 'admin':
                create_usertable()
                vote_table()
                st.success("Logged In as {}".format(username))
                st.subheader("Select Action")
                opt = st.selectbox("Action", ["View All Users", "View All Votes"])
                if opt == "View All Users":
                    result = view_all_users()
                    df = pd.DataFrame(result,columns=['Username','Password','email','DOB','Gender','Area','Aadr','voterid','mobilenumber','time'])
                    st.dataframe(df)
                elif opt == "View All Votes":
                    part = st.selectbox("Party", parties)
                    result = get_votes(part)
                    df = pd.DataFrame(result,columns=['Username','Party','password'])
                    st.dataframe(df['Username'])
                    votes = []
                    # plot a pie chart of the votes received by each party and display the winner
                    for party in parties:
                        votes.append(len(get_votes(party)))
                    st.subheader("Voting Results")
                    st.write("BJP: ", votes[0])
                    st.write("INC: ", votes[1])
                    st.write("AAP: ", votes[2])
                    st.write("Summary")
                    st.write("Total Votes excluding NOTA: ", sum(votes))
                    if votes[0] == votes[1] == votes[2] or votes[0] == votes[1] or votes[0] == votes[2] or votes[1] == votes[2]:
                        st.write("Tie")
                        st.warning("Note: In case of a tie, the winner will be decided by the Election Commission of India.")

                    else:
                        st.write("Current Leading Party: ", parties[votes.index(max(votes))])
                        st.write("Votes: ", max(votes))
                        st.write("Percentage: ", round(max(votes)/sum(votes)*100, 2), "%")
                    fig = plt.figure()
                    plt.pie(votes, labels=parties)
                    plt.axis('equal')
                    st.pyplot(fig)

            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:
                st.write("Logged In as {}".format(username))
                vote_table()
                # check if the user has already voted
                if check_vote(username,hashed_pswd):
                    st.error("You have already voted, Now go back home and wait for the results.")
                    an = animation('https://assets3.lottiefiles.com/packages/lf20_szusawu8.json')
                    plot(an)
                    st.stop()
                else:
                    img = st.camera_input("Image", key="image")
                    if img is not None:

                        img = Image.open(img)
                        img = np.array(img)
                        filename = '{}.jpg'.format(username+'1')
                        cv2.imwrite(filename, img)

                        frst = cv2.imread('{}.jpg'.format(username))
                        frst = cv2.cvtColor(frst, cv2.COLOR_BGR2RGB)
                        frst = face_recognition.face_encodings(frst)[0]

                        sec = cv2.imread('{}.jpg'.format(username+'1'))
                        sec = cv2.cvtColor(sec, cv2.COLOR_BGR2RGB)
                        if len(face_recognition.face_encodings(sec)) == 0:
                            st.error("No Face Detected in the Image")
                            st.success("Please Try Again in a well lit area")
                            return
                        else:
                            sec = face_recognition.face_encodings(sec)[0]

                        res = face_recognition.compare_faces([frst], sec, tolerance=0.4)

                        if res[0] == True:
                            st.success("Face Matched")
                            mob = get_mobilenumber(username,check_hashes(password,hashed_pswd))
                            mob = mob[0][0]
                            mob = '+91'+mob

                            toNumber = mob
                            print(toNumber)
                            sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications"
                            payload = {
                                "identity": {
                                    "type": "number",
                                    "endpoint": toNumber
                                },
                                "method": "sms"
                            }
                            headers = {"Content-Type": "application/json"}
                            response = requests.post(sinchVerificationUrl, json=payload, headers=headers, auth=(applicationKey, applicationSecret))
                            data = response.json()

                            if data:
                                print(data)
                                otp1 = st.text_input("Enter OTP that you have received")
                                party = st.selectbox("Select Party", parties)
                                if st.checkbox("Vote"):
                                    sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications/number/" + toNumber
                                    payload = {
                                        "method": "sms",
                                        "sms": {
                                            "code": otp1
                                        }
                                    }
                                    headers = {"Content-Type": "application/json"}
                                    response = requests.put(sinchVerificationUrl, json=payload, headers=headers, auth=(applicationKey, applicationSecret))
                                    data = response.json()
                                    if data['status'] == 'SUCCESSFUL':
                                            st.success("OTP Verification Successfull")
                                            st.success("Vote added successfully")
                                            vote_table()
                                            add_vote(username,party,hashed_pswd)
                                            os.remove('{}.jpg'.format(username))
                                            os.remove('{}.jpg'.format(username+'1'))
                                                
                                    else:
                                            st.warning("Incorrect OTP")
                        else:
                            st.warning("Face Not Matched ")
            else:
                st.warning("Incorrect Username/Password")
            
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        email = st.text_input("Email")
        dob = st.number_input("Year of Birth", max_value=2005, value=1999, step=1)
        gender = st.selectbox("Gender",['Male','Female','Others'])
        area = st.text_input("Area")
        aadr = st.number_input("Aadhar Number (12 digits)", value=123456789012, step=1)
        voterid = st.text_input("Voter ID")
        mobilenumber = st.text_input("Mobile Number (10 digits)")
        st.error("Enter a valid mobile number as you will receive OTP on this number while voting")
        image = st.camera_input("Image", key="image")
        time = datetime.datetime.now()
        if image is not None:
            filename = "{}.jpg".format(new_user)
            image = Image.open(image)
            image = np.array(image)
            cv2.imwrite(filename, image)

        if st.button("Signup"):
            # check if user already exists with same aadhar number and voter id
            create_usertable()
            if check_user(aadr,voterid):
                st.error("User already exists with same Aadhar Number and Voter ID, No Rigging chinna")
                st.stop()
            else:
                if aadr in aadar:
                    # get id of the aadhar number from list
                    id = aadar.index(aadr)
                    votr = voteid[id]
                    if voterid == str(votr):
                        create_usertable()
                        hashed_new_password = make_hashes(new_password)
                        add_userdata(new_user,hashed_new_password,email,dob,gender,area,aadr,voterid,mobilenumber,time)
                        st.success("You have successfully created a valid Account for voting")
                        st.info("Go to Login Menu to login and vote")
                    else:
                        st.error("Aadhar Number and Voter ID do not match each other ra saami")
                else:
                    st.error("Enter a valid Aadhar Number ra babu")

if __name__ == '__main__':
    main()