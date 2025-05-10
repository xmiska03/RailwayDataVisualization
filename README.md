To run the web app:

source myenv/bin/activate

python3 app.py

To rebundle the JS scripts:

npx webpack

To generate the documentation:

jsdoc scripts/visualization.js -d documentation/visualization_js
