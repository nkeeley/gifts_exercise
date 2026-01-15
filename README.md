# gifts_exercise

## Environment Setup

### Creating a Virtual Environment

1. **Create the virtual environment:**
   ```bash
   python3 -m venv gifts_exercise
   ```
   This creates a directory called `gifts_exercise` with the virtual environment files.

2. **Activate the virtual environment:**
   ```bash
   source gifts_exercise/bin/activate
   ```
   After activation, your prompt should show `(gifts_exercise)`.

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the installation:**
   ```bash
   which python
   ```
   This should point to a path inside the `gifts_exercise` directory.

5. **Deactivate when done:**
   ```bash
   deactivate
   ```

### Notes

- The `gifts_exercise/` directory is already included in `.gitignore` and will not be committed to version control.
- Make sure to activate the virtual environment before working on the project or running notebooks.