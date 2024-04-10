import tkinter as tk

class UserDetailsForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Job Advisor")
        self.geometry("400x300")

        self.sections = [
            {"name": "About", "subfields": []},
            {"name": "Certifications", "subfields": ["meta", "subtitle", "title"]},
            {"name": "Country Code", "subfields": []},
            {"name": "Current Company", "subfields": ["company_id", "industry", "link", "name", "title"]},
            {"name": "Education", "subfields": ["degree", "end_year", "field", "meta", "start_year", "title", "url"]},
            {"name": "Experience",
             "subfields": ["Company", "Company ID", "Description", "Duration", "Location", "End Date",
                           "Duration Short"]},
            {"name": "Languages", "subfields": ["Title", "Subtitle"]},
            {"name": "Position", "subfields": []},
            {"name": "Courses", "subfields": ["Title", "Subtitle"]},
            {"name": "Work Preference", "subfields": ["Location", "Job Type",'Keywords','Profile_URL']},
        ]

        # Initialize user details dictionary with default values
        self.user_details = {}
        for section in self.sections:
            self.user_details[section["name"]] = {subfield: "" for subfield in section["subfields"]}

        self.current_section = 0
        self.create_widgets()

    def create_widgets(self):
        section = self.sections[self.current_section]
        self.label = tk.Label(self, text=section["name"])
        self.label.pack()

        if section["subfields"]:
            self.subfields_entries = {}
            for subfield in section["subfields"]:
                label = tk.Label(self, text=subfield)
                label.pack()
                entry = tk.Entry(self)
                entry.pack()
                self.subfields_entries[subfield] = entry

        else:
            self.entry = tk.Entry(self)
            self.entry.pack()

        self.next_button = tk.Button(self, text="Next", command=self.next_section)
        self.next_button.pack()

        self.submit_button = tk.Button(self, text="Submit", command=self.submit_details, state=tk.DISABLED)
        self.submit_button.pack()

    def next_section(self):
        section = self.sections[self.current_section]
        if section["subfields"]:
            # Update user_details dictionary with entries for the current section's subfields
            self.user_details[section["name"]] = {subfield: entry.get() for subfield, entry in
                                                  self.subfields_entries.items()}
        else:
            # Update user_details dictionary with entry for the current section
            self.user_details[section["name"]] = self.entry.get()

        if self.current_section < len(self.sections) - 1:
            self.current_section += 1
            self.refresh_widgets()
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def refresh_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

    def submit_details(self):
        section = self.sections[self.current_section]
        if section["subfields"]:
            self.user_details[section["name"]] = {subfield: entry.get() for subfield, entry in
                                                  self.subfields_entries.items()}
        else:
            self.user_details[section["name"]] = self.entry.get()

        # Close the UI
        self.destroy()

    def get_user_details(self):
        return self.user_details



