<h1>NLP Text Data Analysis</h1><br>
<p>
This project leverages new Large Language Models from OpenAI to analyze data by creating a SQL query from a user asking a question in natural language and that SQL query will then query the database to produce the final output.
</p>
<p>
The demo of this code is located <a href='https://madsteam.pythonanywhere.com/example3/'>here</a>.
</p>
<p>
The Web App and postgres database are currently hosted on PythonAnywhere.com.
</p>
<p>
Read the full report <a href='https://docs.google.com/document/d/1iwomwkDXeGCfXZMS-bf3sui0GaBkR70tCN9BwpwSig0/edit#'>here</a>.

<h2>Getting Started</h2>
<p>
Clone the repo via git clone https://github.com/Wenjun-Mao/siads699.git<br>
</p>
<p>
Install python package dependencies via pip install -r requirements.txt
</p>
<p>
The folder example3 contains the working code to run the web application.
</p>
<p>
These two files are used to replicate data the QA and visuals in the project:
</p>
<p>
01-Python-QA-File.py<br>
02-Python-Visuals.ipynb
</p>
<h2>Data Access</h2>

<p>
Data supporting this research is available at https://archive.ics.uci.edu/ml/datasets/online+retail
</p>
<p>
Citation: Dua, D. and Graff, C. (2019). UCI Machine Learning Repository [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California, School of Information and Computer Science.
</p>
<p>
We did adjusted the columns for usability and readability. Specifically, we adjusted the dates so they were recent, renamed the countries to local cities in the US, and included hypothetical customer names instead of the 5 digit code.
</p>