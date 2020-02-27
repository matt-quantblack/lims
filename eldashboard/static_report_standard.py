from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, data, *args, **kwargs):
        super(PDF, self).__init__(*args, **kwargs)
        self.data = data

    def header(self):
        data = self.data

        self.set_font("Arial", size=6)

        self.cell(20, 3, "Job {}".format(data["header_fields"]["Job_Id"]), ln=0, align='L')
        self.cell(120)
        self.cell(55, 3, "Report auto-generated by EL LIMS on {}".format(data["header_fields"]["Now"]), ln=1, align='L')

        self.image("./eldashboard/media/header.jpg", x=10, y=16, w=120)

        self.set_font("Arial", size=10)

        align_to = 130
        self.ln(1)
        self.cell(align_to)
        self.cell(65, 4, "Phone: {}".format(data["header_fields"]["Company_Phone"]), ln=1, align='L')
        self.cell(align_to)
        self.cell(65, 4, "Email: {}".format(data["header_fields"]["Company_Email"]), ln=1, align='L')
        self.cell(align_to)
        self.cell(65, 4, "Web: {}".format(data["header_fields"]["Company_Web"]), ln=1, align='L')
        self.cell(0, 4, ln=1)
        self.cell(align_to)
        self.cell(65, 4, data["header_fields"]["Company_Address1"], ln=1, align='L')
        self.cell(align_to)
        self.cell(65, 4, data["header_fields"]["Company_Address2"], ln=1, align='L')

        self.cell(75, 4, "Customer: {}".format(data["header_fields"]["Sample_Client_Name"]), ln=1, align='L')
        self.cell(75, 4, data["header_fields"]["Sample_Client_Full_Address"], ln=1, align='L')

    def footer(self):
        data = self.data

        self.set_y(-20)

        self.set_font("Arial", size=8)

        self.cell(20, 3, "Test Report")
        self.cell(110)
        self.cell(30, 3, "Electronically signed", ln=1)

        self.cell(40, 3, "Authorised By {}".format(data["header_fields"]["TestOfficer"]), ln=1)

        self.cell(20, 3, data["header_fields"]["Title"])
        self.cell(110)
        self.cell(30, 3, "Signed on: {}".format(data["header_fields"]["Now"]), ln=1)

        self.ln(2)

        self.set_font("Arial", size=6)
        self.multi_cell(190, 2,
                        "The data pertains solely to the samples tested. The homogeneity or the sampling of the samples cannot be guaranteed and therefore may not be representative of the lot or batch or other samples. Consequently the data may not necessarily justify the acceptance or rejection of a lot or batch, a product recall or support legal proceedings. It is the responsibility of the client to provide all information relevant to the analysis requested. This report does not imply that Enzyme Labs has been engaged to consult upon the consequences of the analysis and for any action that should be taken as a result of the analysis. This report must be reproduced in full unless written permission is obtained from Enzyme Labs.")


def generate_report(data, outpath):
    pdf = PDF(data)
    # for each sample add a page
    col1 = 29
    col2 = 68
    col3 = col1
    col4 = col2 + 1
    cell_height = 6
    for sample in data["samples"]:
        pdf.add_page()

        # sample details
        pdf.ln(cell_height)

        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col1, cell_height, "Sample:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col2, cell_height, sample["fields"]["Sample_Name"], align="L", border=1)
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col3, cell_height, "Condition:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col4, cell_height, sample["fields"]["Sample_Condition"], align="L", border=1, ln=1)

        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col1, cell_height, "Client Ref:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col2, cell_height, sample["fields"]["Sample_ClientRef"], align="L", border=1)
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col3, cell_height, "Description:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col4, cell_height, sample["fields"]["Sample_Description"], align="L", border=1, ln=1)

        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col1, cell_height, "Batch:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col2, cell_height, sample["fields"]["Sample_Batch"], align="L", border=1)
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col3, cell_height, "Receipt Date:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col4, cell_height, sample["fields"]["Sample_Received"], align="L", border=1, ln=1)

        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col1, cell_height, "EL Ref:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col2, cell_height, "# {}".format(sample["fields"]["Sample_Id"]), align="L", border=1)
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(col3, cell_height, "Job Number:", align="L", border=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(col4, cell_height, data["header_fields"]["Job_Id"], align="L", border=1, ln=1)

        pdf.ln(cell_height)

        # test details
        testc1 = 80
        testc2 = 40
        testc3 = 25
        testc4 = 50

        pdf.set_font("Arial", "B", size=12)
        pdf.cell(testc1, cell_height, "Method", align="L", border=1)
        pdf.cell(testc2, cell_height, "Result", align="L", border=1)
        pdf.cell(testc3, cell_height, "Units", align="L", border=1)
        pdf.cell(testc4, cell_height, "Details", align="L", border=1, ln=1)

        y = pdf.get_y()
        x = pdf.get_x()

        for test in sample["tests"]:
            pdf.set_font("Arial", size=12)
            pdf.set_xy(x, y)
            pdf.multi_cell(testc1, cell_height, test["Method"], align="L", border=0)
            pdf.set_xy(x + testc1, y)
            pdf.multi_cell(testc2, cell_height, test["Result"], align="L", border=0)
            pdf.set_xy(x + testc1 + testc2, y)
            pdf.multi_cell(testc3, cell_height, test["Units"], align="L", border=0)
            pdf.set_font("Arial", size=8)
            pdf.set_xy(x + testc1 + testc2 + testc3, y)
            pdf.multi_cell(testc4, 4, test["Details"], align="L", border=0)

            height = pdf.get_y() - y
            pdf.rect(x, y, testc1, height)
            pdf.rect(x + testc1, y, testc2, height)
            pdf.rect(x + testc1 + testc2, y, testc3, height)
            pdf.rect(x + testc1 + testc2 + testc3, y, testc4, height)

            y = pdf.get_y()

    pdf.output(outpath)
