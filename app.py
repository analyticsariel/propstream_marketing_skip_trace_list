import streamlit as st
import pandas as pd


def merge_files(df_contacts, df_list):
    """
    Merge marketing and contacts tables
    """
    df_c = df_contacts.drop(columns=['Street Address', 'City', 'State', 'Zip'])
    df_c = df_c.rename(columns={'First Name': 'Owner 1 First Name', 
                                        'Last Name': 'Owner 1 Last Name', 
                                        'Mail Street Address': 'Mailing Address', 
                                        'Mail City': 'Mailing City', 
                                        'Mail State': 'Mailing State', 
                                        'Mail Zip': 'Mailing Zip'})
    return pd.merge(
        df_list, 
        df_c, 
        on=['Owner 1 First Name', 'Owner 1 Last Name', 'Mailing Address', 
            'Mailing City', 'Mailing State', 'Mailing Zip'], 
        how='left')


@st.cache
def convert_df(df):
    """
    Dataframe to CSV
    """
    return df.to_csv().encode('utf-8')


st.markdown('# PropStream Merge Leads and Contacts')
st.markdown('_This tool merges the [Marketing List](https://www.propstream.com/how-to-save-a-marketing-list) and [Skip Tracing List](https://www.propstream.com/how-to-skiptrace-a-list#:~:text=Real%20estate%20professionals%20skip%20trace,on%20the%20%E2%80%9CContacts%E2%80%9D%20page.) in PropStreams._')

# uploads
mrk_list_upload_file = st.file_uploader('STEP 1: Upload Marketing List from PropStream')
contacts_list_upload_file = st.file_uploader('STEP 2: Upload Skip Tracing Contact List from PropStream')

# check if files are uploaded
if mrk_list_upload_file is not None:
    df_list = pd.read_excel(mrk_list_upload_file)

if contacts_list_upload_file is not None:
    df_contacts = pd.read_csv(contacts_list_upload_file)
    # get file name
    contacts_fn = contacts_list_upload_file.name
    contacts_fn = contacts_fn.split('-')[-1].split('.')[0]

if st.button('Merge'):
    if (mrk_list_upload_file is not None) & (contacts_list_upload_file is not None):
        # merge files
        df_merge = merge_files(df_contacts, df_list)
        # summary stats
        col1, col2, col3 = st.columns(3)
        col1.metric('Number of Leads', len(df_merge))
        try:
            cnt_cell = len(df_merge.loc[~df_merge['Cell'].isnull()])
        except:
            cnt_cell = 0
        skip_trace_cell_prct = str(int(cnt_cell / len(df_merge) * 100)) + '%'
        col2.metric('% Skip Traced Cell', skip_trace_cell_prct)
        try:
            cnt_email = len(df_merge.loc[~df_merge['Email 1'].isnull()])
        except:
            cnt_email = 0
        skip_trace_email_prct = str(int(cnt_email / len(df_merge) * 100)) + '%'
        col3.metric('% Skip Traced Email', skip_trace_email_prct)
        # download button
        csv_merge = convert_df(df_merge)
        st.download_button("Download", 
                            csv_merge, 
                            "marketing_skip_trace_{}.csv".format(contacts_fn),
                            "text/csv",
                            key='download-csv'
                            )
        # output
        st.dataframe(df_merge.head(10)) # show first 10
    elif (mrk_list_upload_file == None) & (contacts_list_upload_file is not None):
        st.error('Please upload the Marketing List file')
    elif (mrk_list_upload_file is not None) & (contacts_list_upload_file == None):
        st.error('Please upload the Skip Tracing List file')
    else:
        st.error('Please upload the Marketing List AND Skip Tracing List file')
            