import PyPDF2, re


def read_pdf(filename):
    object = PyPDF2.PdfFileReader(filename, strict=False)
    NumPages = object.getNumPages()
    pattern = ["DACTE", "CT-E", 'CTE', 'CTe', 'cte',
               'DANFE', 'DANFe', 'NF-E', 'NF-e', 'NFE', 'nfe']
    results = []
    code = []
    for i in range(0, NumPages):
        PageObj = object.getPage(i)
        page = PageObj.extractText()
        # Search for pattern in page
        results.extend(re.findall(r"(?=("+'|'.join(pattern)+r"))", page))
        # Search for code with 44 digits
        for word in page.splitlines():
            if any(char.isdigit() for char in word) == True:
                if len(word.replace(' ', '')) == 44:
                    code.append(word.replace(' ', ''))
    # checks if 'results' are CTE or NFE.
    if any(x in results for x in ["DACTE", "CT-E", 'CTE', 'CTe', 'cte']) == True:
        consult_type = 'cte'
    elif any(x in results for x in  ['DANFE', 'DANFe', 'NF-E', 'NF-e', 'NFE', 'nfe']) == True:
        consult_type = 'nfe'
    return (code[0], consult_type)