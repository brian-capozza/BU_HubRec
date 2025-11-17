from django.db import models

HUB_CHOICES = [
    ("PLM", "Philosophical Inquiry and Life's Meanings"),
    ("AEX", "Aesthetic Exploration"),
    ("HCO", "Historical Consciousness"),
    ("SI1", "Scientific Inquiry I"),
    ("SI2", "Scientific Inquiry II"),
    ("SO1", "Social Inquiry I"),
    ("SO2", "Social Inquiry II"),
    ("QR1", "Quantitative Reasoning I"),
    ("QR2", "Quantitative Reasoning II"),
    ("IIC", "The Individual in Community"),
    ("GCI", "Global Citizenship and Intercultural Literacy"),
    ("ETR", "Ethical Reasoning"),
    ("FYW", "First-Year Writing Seminar"),
    ("WRI", "Writing, Research, and Inquiry"),
    ("WIN", "Writing-Intensive Course"),
    ("OSC", "Oral and/or Signed Communication"),
    ("DME", "Digital/Multimedia Expression"),
    ("CRT", "Critical Thinking"),
    ("RIL", "Research and Information Literacy"),
    ("TWC", "Teamwork/Collaboration"),
    ("CRI", "Creativity/Innovation"),
]

COLLEGE_CHOICES = [
    ("BUA", "BU Academy"),
    ("CDS", "Faculty of Computing and Data Science"),
    ("CAS", "College of Arts and Sciences"),
    ("COM", "College of Communication"),
    ("ENG", "College of Engineering"),
    ("CFA", "College of Fine Arts"),
    ("CGS", "College of General Studies"),
    ("QST", "Questrom School of Business"),
    ("SAR", "Sargent College of Health and Rehabilitation"),
    ("SHA", "School of Hospitality Administration"),
    ("SPH", "School of Public Health"),
    ("WED", "Wheelock College of Education"),
    ("MET", "Metropolitan College"),
    ("KHC", "Kilichand Honors College"),

    # ("SDM", "School of Dental Medicine"),
    # ("GMS", "School of Medicine"),
    # ("LAW", "School of Law"),
    # ("SSW", "School of Social Work"),
    # ("STH", "School of Theology"),
]

SUBJECT_CHOICES = [
    ("BU", "BU Academy"),
    ("AA", "African American Studies"),
    ("AH", "History of Art & Arch"),
    ("AM", "American Studies"),
    ("AN", "Anthropology"),
    ("AR", "Archaeology"),
    ("AS", "Astronomy"),
    ("BB", "Biochem & Molecular Bio"),
    ("BI", "Biology"),
    ("CC", "Core Curriculum"),
    ("CG", "Modern Greek"),
    ("CH", "Chemistry"),
    ("CI", "Cinema & Media Studies"),
    ("CL", "Classical Studies"),
    ("CN", "Neuroscience"),
    ("CS", "Computer Science"),
    ("EC", "Economics"),
    ("EE", "Earth & Environment"),
    ("EI", "Editorial Studies"),
    ("EN", "English"),
    ("FY", "First Year Experience"),
    ("HI", "History"),
    ("ID", "Interdisciplinary Stds"),
    ("IN", "Internship"),
    ("IR", "International Relations"),
    ("JS", "Jewish Studies"),
    ("LC", "Mod Lang Chinese"),
    ("LD", "Mod Lang African Lng&Lin"),
    ("LE", "Mod Lang Swahili"),
    ("LF", "Mod Lang French"),
    ("LG", "Mod Lang German"),
    ("LH", "Mod Lang Hebrew"),
    ("LI", "Mod Lang Italian"),
    ("LJ", "Mod Lang Japanese"),
    ("LK", "Mod Lang Korean"),
    ("LM", "Mod Lang isiXosha"),
    ("LN", "Mod Lang Hindi-Urdu"),
    ("LO", "Mod Lang Yoruba"),
    ("LP", "Mod Lang Portuguese"),
    ("LR", "Mod Lang Russian"),
    ("LS", "Mod Lang Spanish"),
    ("LT", "Mod Lang Turkish"),
    ("LW", "Mod Lang Wolof Akan Twi"),
    ("LX", "Linguistics"),
    ("LY", "Mod Lang Arabic"),
    ("LZ", "Mod Lang Persian (Farsi)"),
    ("MA", "Mathematics & Statistics"),
    ("MB", "Mol Bio, Cell Bio, BioCh"),
    ("MR", "Marine Science"),
    ("NE", "Neuroscience"),
    ("NS", "Natural Sciences"),
    ("PH", "Philosophy"),
    ("PO", "Political Science"),
    ("PS", "Psychological & BrainSci"),
    ("PY", "Physics"),
    ("RN", "Religion"),
    ("SO", "Sociology"),
    ("SY", "Senior Year Experience"),
    ("TL", "World Languages & Lit"),
    ("WR", "Writing Program"),
    ("WS", "Women Gender & Sexuality"),
    ("XL", "Comparative Literature"),
    ("BF", "Bioinformatics"),
    ("DS", "Computing & Data Science"),
    ("DX", "Data Science Online"),
    ("AR", "Visual Arts"),
    ("DA", "Dance"),
    ("FA", "Fine Arts"),
    ("ME", "Music"),
    ("MH", "Music"),
    ("ML", "Applied Music Lessons"),
    ("MP", "Music"),
    ("MT", "Music"),
    ("MU", "Music"),
    ("TH", "Theatre"),
    ("HU", "Humanities"),
    ("IN", "Independent Study"),
    ("IS", "Interdisciplinary Stds"),
    ("MA", "Mathematics"),
    ("NS", "Natural Sciences"),
    ("SS", "Social Sciences"),
    ("CM", "Mass Comm, Advert & PR"),
    ("CO", "Communications Core"),
    ("FT", "Film & Television"),
    ("JO", "Journalism"),
    ("PR", "Public Relations"),
    ("EC", "Electrical & Comp Engr"),
    ("EK", "Engineering Core"),
    ("ME", "Mechanical Engineering"),
    ("MS", "Materials Science & Engr"),
    ("SE", "Systems Engineering"),
    ("AC", "Academic Community"),
    ("CO", "Communication"),
    ("EL", "English Language"),
    ("EN", "English Lang & Orientatn"),
    ("GS", "Grammar and Vocabulary"),
    ("LS", "Listening & Speaking"),
    ("ME", "Media Studies"),
    ("OR", "Orientation"),
    ("RW", "Reading & Writing"),
    ("SL", "Speaking & Listening"),
    ("TP", "Test Preparation"),
    ("CC", "Cocurricular"),
    ("FY", "First Year Experience"),
    ("IC", "Interdisciplinary"),
    ("RL", "Research & Info Literacy"),
    ("SJ", "Social Justice"),
    ("XC", "Cross-College Challenge"),
    ("AH", "History of Art & Arch"),
    ("AM", "Am & New England Studies"),
    ("AN", "Anthropology"),
    ("BI", "Biology"),
    ("EN", "English"),
    ("HC", "Honors College"),
    ("HI", "History"),
    ("IR", "International Relations"),
    ("PY", "Physics"),
    ("RH", "Rhetoric"),
    ("ST", "Studio"),
    ("AD", "Administrative Sciences"),
    ("AH", "Art History"),
    ("AN", "Anthropology"),
    ("AR", "Arts Administration"),
    ("AT", "Actuarial Science"),
    ("BB", "Biochem & Molecular Bio"),
    ("BI", "Biology"),
    ("CH", "Chemistry"),
    ("CJ", "Criminal Justice"),
    ("CS", "Computer Science"),
    ("HC", "Health Communication"),
    ("HI", "History"),
    ("IS", "Interdisciplinary Stds"),
    ("LX", "Linguistics"),
    ("MA", "Mathematics & Statistics"),
    ("MG", "Management"),
    ("PH", "Philosophy"),
    ("PS", "Psychology"),
    ("PY", "Physics"),
    ("UA", "Urban Affairs"),
    ("AS", "Aerospace Studies"),
    ("MS", "Military Science"),
    ("NS", "Naval Science"),
    ("AC", "Accounting"),
    ("BA", "Business Analytics"),
    ("BE", "Business Economics"),
    ("ES", "Executive Skills"),
    ("FE", "Finance"),
    ("IM", "International Management"),
    ("IS", "Mgmt Information Systems"),
    ("LA", "Law"),
    ("MK", "Marketing"),
    ("MO", "Organizational Mgmt"),
    ("OM", "Operations & Tech Mgmt"),
    ("QM", "Quantitative Modeling"),
    ("SI", "Strategy & Innovation"),
    ("SM", "Management Core"),
    ("HP", "Health Professions"),
    ("HS", "Health Sciences"),
    ("OT", "Occupational Therapy"),
    ("PT", "Physical Therapy"),
    ("SH", "Speech, Lang&Hearing Sci"),
    ("AH", "Hospitality Admin"),
    ("PH", "General Public Health"),
    ("BI", "English as a Second Lang"),
    ("CE", "Counseling/Counsel Psych"),
    ("CF", "Curriculum & Teaching"),
    ("CH", "Childhood Education"),
    ("CL", "Child Life/Fam Cent Care"),
    ("CT", "Curriculum & Teaching"),
    ("DE", "Deaf Studies"),
    ("DS", "Human Dev & Education"),
    ("EC", "Early Childhood Educ"),
    ("ED", "Education"),
    ("EN", "English & Lang Arts Educ"),
    ("HD", "Human Dev & Education"),
    ("LR", "Reading"),
    ("LS", "Language & Literacy Stds"),
    ("ME", "Mathematics Education"),
    ("PE", "Physical Ed & Coaching"),
    ("SC", "Science Education"),
    ("SE", "Special Education"),
    ("SO", "Social Studies Education"),
    ("TL", "TESOL & Mod Foreign Lang"),
    ("WL", "Language Teaching"),
    ("YJ", "Youth Justice"),
    ("A1", "At at BU"),
    ("BD", "Cross-Reg Brandeis Univ"),
    ("BO", "Cross-Reg Boston College"),
    ("HC", "Cross-Reg Hebrew College"),
    ("TF", "Cross-Reg Tufts Univ"),
    ("UC", "*UNKNOWN*")
]

class Professor(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)
    rating = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return self.name

class Hub(models.Model):
    unit_name = models.CharField(null=False, blank=False, choices=HUB_CHOICES, max_length=3, unique=True)

    def __str__(self):
        return self.unit_name

class ClassData(models.Model):
    college = models.CharField(null=False, blank=False, choices=COLLEGE_CHOICES, max_length=3)
    subject = models.CharField(null=False, blank=False, choices=SUBJECT_CHOICES, max_length=2)
    catalog_number = models.CharField(null=False, blank=False, max_length=5)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'subject', 'catalog_number'],
                name='unique_classdata'
            )
        ]
        verbose_name_plural = 'Class Data'

    def __str__(self):
        return f'{self.college} {self.subject}{self.catalog_number}'

class Course(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)
    description = models.TextField(null=False, blank=False, default='')
    credits = models.CharField(null=False, blank=True, max_length=10, default=4)

    class_data = models.ForeignKey(ClassData, on_delete=models.CASCADE)
    hubs = models.ManyToManyField(Hub)
    class_data = models.ManyToManyField(Professor)

    def __str__(self):
        hubs_list = ", ".join(str(h) for h in self.hubs.all())
        return (
            f"Course Number: {self.class_data}\n"
            f"Course Name: {self.name}\n"
            f"Credits: {self.credits}\n"
            f"Hubs Fulfilled: {hubs_list}\n"
            f"Course Description: {self.description}"
        )