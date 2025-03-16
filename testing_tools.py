import pandas as pd
from io import StringIO
import json
import os
import regex as re
import numpy as np



def yyyymmdd_date(date):
    '''takes str object or datetime object as in: datetime.date.today()'''
    if type(date)==str:
        if "-" in date:
            date = date.split("-")
            year = int(date[0])
            month = int(date[1])
            day = int(date[2])
    else:
        day = date.day
        month = date.month
        year = date.year
    if len(str(year))!=4:
        raise Exception("Date formatting error.")
    if day<10:
        day = "0"+str(day)
    day = str(day)
    if month<10:
        month = "0"+str(month)
    month = str(month)
    return str(year)+month+day


#file saving
def check_s3_file_exists(s3_client, bucket, key):
    """Documentation:
    Check if a file exists in S3, using  boto3 s3_client
    Works with Digital Ocean and probably amazon"""
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except s3_client.exceptions.ClientError:
        return False

def get_new_path_if_exists(path, s3_client, bucket='margingeek'):
    """Modify the path to avoid overwriting existing files by appending a counter"""
    original_path = path
    counter = 1
    file_name, file_extension = os.path.splitext(path)
    # Continue checking if file exists, append (1), (2), etc., to avoid overwriting
    while check_s3_file_exists(s3_client, bucket, path) and counter <10:
        path = f"{file_name}({counter}){file_extension}"
        counter += 1
    return path



def title_case(text):
    'Alternative to title function for capitalizing words in title according to English capitalization standards'
    if text is None:
        return text
    small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'of'}
    words = str(text).split()
    if len(words)==0:
        return text
    result = [words[0].capitalize()]  # Capitalize the first word
    if len(words)>2:
        for word in words[1:-1]:
            if word.lower() in small_words:
                result.append(word.lower())  # Don't capitalize small words
            else:
                result.append(word.capitalize())  # Capitalize everything else    
    if len(words) > 1:
        result.append(words[-1].capitalize())    
    return ' '.join(result)


def read_csv_from_server(path,*args,cloud=False,s3_client=None,case_insensitive=False,strip=False,title_case_=False,**kwargs):
    '''Documentation
    pandas read_csv wrapper for our digital ocean s3 bucket, which mirrors the same path structure.
    Case insensitive reading is required for using column mapping, currently implemented for dtype column. 
    We can pass any case to dtype and it will find the matching column name in the csv being read
    
    Used across the application: i.e., app.py, product_scanner, and more.

    input: path or file_buffer
    case_insensitive: converts to title case
    strip: ignores leading and trailing spaces in column header and in dtype

    Approach: We import the data twice, so that dtype and case sensitivity settings are applied BEFORE running dtype = {}. 
    The first import handles all columns as string.  
    
    output csv'''
    def get_file_object(path):
        if cloud:
            response = s3_client.get_object(Bucket='margingeek', Key=path)
            try:
                return StringIO(response['Body'].read().decode('utf-8'))
            except UnicodeDecodeError:
                pass
                #tbd
                #return StringIO(response['Body'].read().decode('latin1?'))
        else:
            return path
    file_obj = get_file_object(path)
    dtype = kwargs.pop('dtype', None)
    index_col = kwargs.pop('index_col', None)
    df = pd.read_csv(file_obj, *args, dtype=str,**kwargs,na_filter=False)
    #df = pd.read_csv(file_obj, dtype=str,index_col = 0,na_filter=False)


    if strip:
        df.columns = df.columns.str.strip()
    if case_insensitive:
        df.columns = df.columns.str.lower()

    # Step 3: Identify and rename any columns in dtype
    new_dtype = {}
    if isinstance(dtype,dict):
        for d_col,d_v in dtype.items():
            if strip:
                d_col = str(d_col).strip()
            if case_insensitive:
                d_col = str(d_col).lower()
            new_dtype[d_col] = d_v
    if len(new_dtype.keys()) == 0:
        new_dtype = None

    # Step 4: Save to an in-memory object and re-import with specified dtype for 'code'
    new_buffer = StringIO()
    df.to_csv(new_buffer, index=False)
    skiprows = kwargs.pop('skiprows', None)
    new_buffer.seek(0)  # Move to the start of the buffer

    # Step 5: Re-import with dtype specified for the 'code' column
    if index_col is not None:
        kwargs['index_col'] = index_col
    df_final = pd.read_csv(new_buffer, *args, dtype=new_dtype, **kwargs)
    if title_case_:
        df_final.columns = list(map(lambda x: title_case(x), df_final.columns))
    return df_final

def read_file_from_server(path,*args,cloud=True,s3_client =None,filetype=None,**kwargs):
    '''Documentation: 
    reads from server or local. Specify filetype for standard processes
    .json: runs jsonloads
    .txt: default
    .csv: uses pandas.read_csv and passes all *args and **kwargs

    set cloud = True to read from server

    Assumes server is s3-like. i.e., works with digital ocean spaces.
    '''
    if cloud:
        response = s3_client.get_object(Bucket='margingeek',Key=path)
        content = response['Body'].read().decode('utf-8')
        if filetype == '.json' or filetype == 'json':
            content = json.loads(content)
        elif filetype == '.txt':
            content = str(content)
        elif filetype == '.csv' or filetype == 'csv':
            buffer = StringIO(content)
            content = pd.read_csv(buffer,*args, **kwargs)#df = pd.read_csv(csv_buffer)
    else:
        if filetype =='.json' or filetype == 'json' or path.endswith('.json'):
            with open(path, 'r') as f:
                content = json.load(f)
        elif filetype == '.txt' or path.endswith('.txt'):
            with open(path,'r') as f:
                content = f.read()
        elif filetype =='.csv' or filetype == 'csv' or path.endswith('.csv'):
            content = pd.read_csv(path,*args,**kwargs)
    return content


def save_txt(path,text,cloud=False, s3_client=None, bypass_overwrite_check=False,write_new_path=False):
    file_path = str(path)
    if file_path[-1] =='/':
        file_path = file_path[:-1]
    if "/" in file_path:
        file_name = file_path.split("/")
        file_name = file_name[-1]
        file_path = file_path[:-len(file_name)]
    else:
        file_name = str(file_path)
        file_path = None
    if cloud:
        if write_new_path:
            file_path = get_new_path_if_exists(file_path, s3_client, bucket='margingeek')
        bypass_overwrite_check = True #it has to be, because we're not going to be there to hit y/n
        file_path = str(file_path).replace("None","")+file_name
        # Create an S3 client using boto3 (DigitalOcean Spaces is S3-compatible)
        # Upload the CSV to DigitalOcean Spaces
        s3_client.put_object(
            Bucket='margingeek',  # Replace with your Space name
            Key=file_path,  # The file file_path within the Space
            Body=text,
            ContentType='text/plain'
        )
        print(f'Saved to s3 margingeek bucket: {file_path}')
    else:
        if bypass_overwrite_check or file_name not in os.listdir(file_path):
            with open(str(file_path).replace("None","")+file_name, 'w') as file:
                file.write(text)
            print("Saved.")
        else:
            decision = input("Overwrite? (y/n)")
            if decision.lower() =="y":
                with open(str(file_path).replace("None","")+file_name, 'w') as file:
                    file.write(text)
                print("Saved.")
            else:
                print("Not saved.")


def convert_to_number(s, replace_na = np.nan,additional_nans = []):
    '''Convert to number. 
    Notes: 
    - if it's a number with minimal cleaning return the number
    - We don't just want to return any of the numbers because there could be two numbers
    - Used for $ and % values, so we want to make sure we're returning the dollar or % value, without returning other number types
    - if you want the first number, you'd run  re.findall('[0-9]+\.?[0-9]*',str(current_suom_price)) or similar without decimal; but i dont think this is good for most of our use cases in case it grabs the wrong number. can run outside of convert_to_number
    '''
    nan_categories = ['na','nan','None','']
    if type(additional_nans)==list and len(additional_nans) >0:
        for nancat in additional_nans:
            nan_categories.append(nancat)

    if type(s) == float or type(s) == np.float64 or type(s)==int or type(s)== np.int64 or s == None:
        if str(s).lower() in ['nan','none','']:
            return replace_na
        else:
            return s
    if str(s).startswith('\''):
        s = str(s).strip("\'")
    if "$" in s:
        usd_pattern = r'\$\s*([0-9,]+\.\d{2})'
        usd_match = re.search(usd_pattern, s)
        if usd_match:
            usd_string = usd_match.group(1)
            usd_string = usd_string.replace(',', '')
            usd_value = float(usd_string)
            return usd_value
    #if no dollar sign, or if that doesn't work, then try the other method 
    s = str(s).replace("$","").replace(",","").replace(" ","").lower()
    
    if s in nan_categories:
        return replace_na
    if "%" in s:
        try:
            s = float(s.replace("%","")) / 100
        except:
            pass
    try:
        return float(s)
    except:
        return replace_na
