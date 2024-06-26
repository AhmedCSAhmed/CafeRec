# CafeRec
The CafeRec application recommends nearby cafes to users based on their location and the "vibe" they prefer. For example, users can specify they want a "calm, quiet" cafe with "good lattes" and CafeRec will provide a list of matching cafes for them.

## Setup
Create a virtual environment and navigate to the repo's root directory. Then run the command:

```bash
pip install -r ./requirements.txt
```

to install all needed dependencies for the project.

To ensure that the most updated set of dependencies are present in the ``` requirements.txt ``` file, 
run the following command in the root project folder before pushing any code to the GitHub repository:

```bash
pip freeze ./requirements.txt
```