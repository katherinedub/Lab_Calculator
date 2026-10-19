
######run with: "python -m streamlit run streamlit_app.py"
#    TO DO: 
#          handle non red/sst/edta. 
#          handle purples if sharing is prohibitted
#          make results look nice
#          handle collection instructions



#=====HEADER=====



import streamlit as st
import sys
import numpy as np
import pandas as pd
import openpyxl
import math

#===== EXAMPLE DATAFRAME ====

#d = {"Test ID": [1, 2], "Test Name": ['example 1', 'example 2'], 'Quantity':[0.5,1]}
#df = pd.DataFrame([[198, 1,'R', False],[567, 2,'R', False],[110, 5,'R', False], [909, 1,'P', False], [261, 6,'P', True], [611, 4,'R', False], [500, 2, 'R', True], [510, 3, 'P',True], [622, 1, 'P', False]], columns=['ID','Quant','Type', 'exclusive'])
#st.dataframe(df)

#===== IMPORT THE REAL DATA =====

df = pd.read_excel("KateTestDirectory.xlsx")
#st.write(df)
# Preview first 5 rows:
# st.write(df.head())
#st.write(df.columns.tolist())
#===== CHOOSE WHICH TYPES CAN SHARE TUBES =====

st.title("Lab Calculator for Medical Assistants")
st.header("created by Katherine Dubovi")
st.divider()
st.subheader("What can this tool do?")
st.write("This tool is designed for medical assistants to calculate the precise number and types of lab specimens to collect. It improves upon the Quest Diagnostics Test Directory by allowing simultaneous multi-test searching and automatically calculating the total number of required specimens. Search results limit information only to what is useful to a medical assistant.")
st.divider()
pair_purple = False
show_details = False
with st.expander(f"**Options:**"):
    pair_purple = st.checkbox(f"**Pair Purple:** Check if labs in EDTA tubes (purple and lavender) can be combined in the same tube, i.e. two EDTA labs can go in the same tube if their combined volume is less than the tube's capacity and neither has special collection instructions preventing combination.")
    show_details = st.checkbox(f"**Detailed Results:** Check to see more details about the lab tests (recommended).")

#===== SEARCHBAR FOR LAB =====
search = st.text_input("Enter test IDs here. Separate entries with a space.") 
#st.write(type(search))
try:
    search_list = list(map(int, search.split()))
except ValueError:
    st.write(f"**Entries must numerical values only.**")
    sys.exit(0)
#st.write(search_list)


#===== CHECKING SEARCH AGAINST DATAFRAME =====
match = df[df.iloc[:,0].isin(search_list).copy()]
match = match.sort_values(by="Volume (ml)")
#st.write(match)

#===== IF SEARCH ENTRIES WEREN'T FOUND =====
if len(search_list) != len(match):
    st.divider()
    st.subheader(f"**Unrecognized IDs entered:**")
    missing_values = [str(x) for x in search_list if x not in df.iloc[:,0].values]
    missing_values_string = ", ".join(map(str, missing_values))
    st.write(missing_values_string)
    st.write(f"**Some test IDs may be missing from this database.** Check that you entered all of your labs properly. If there are no typos, please email Kate Dubovi (katherinedubovi@centraloutreach.com) with the missing lab code. It will be added promptly.")
    st.write('In the meantime, you can find information about your lab from the Quest Diagnostics directory at https://testdirectory.questdiagnostics.com/')
    st.divider()
# ===== CALCULATE TUBES =====
if len(match) > 0:
    SST_count = 0
    big_purple_count = 0
    small_purple_count = 0
    red_count = 0
    st.write('Make sure to check Collection Notes.')
    #etc...
    
# Account for exclusive tubes:  

#----- NOTE: ADD COLLECTION INSTRUCTIONS! -----
    exclusives = match[match['Can Combine']=='N']
    #st.write(exclusives)

    exclusive_SST = exclusives[exclusives['Tube']=='SST']
   # st.write("Exclusive Red:")
   # st.write(exclusive_red)
    SST_count += len(exclusive_SST)
    #st.write(exclusive_SST[exclusive_SST['Collection notes'].str.contains('Requires 2 tubes', case=False)])
    if len(exclusive_SST[exclusive_SST['Collection notes'].str.contains('Requires 2 tubes', case=False)]) >0:
        SST_count += len(exclusive_SST[exclusive_SST['Collection notes'].str.contains('Requires 2 tubes', case=False)])

    exclusive_red = exclusives[exclusives['Tube']=='Red']
       # st.write("Exclusive Red:")
       # st.write(exclusive_red)
    red_count += len(exclusive_red)

    if pair_purple == True:
   # st.write("Exclusive Big Purple:")
        exclusive_big_purple = exclusives[(exclusives['Tube']=='EDTA') & (exclusives['Volume (ml)']>4)]
   # st.write(exclusive_big_purple)
        big_purple_count += len(exclusive_big_purple)

   # st.write("Exclusive Small Purple:")
        exclusive_small_purple = exclusives[(exclusives['Tube']=='EDTA') & (exclusives['Volume (ml)']<=4)]
   # st.write(exclusive_small_purple)
        small_purple_count += len(exclusive_small_purple)
    else:
        exclusive_big_purple = match[(match['Tube']=='EDTA') & (match['Volume (ml)']>4)]
   # st.write(exclusive_big_purple)
        big_purple_count += len(exclusive_big_purple)

   # st.write("Exclusive Small Purple:")
        exclusive_small_purple = match[(match['Tube']=='EDTA') & (match['Volume (ml)']<=4)]
   # st.write(exclusive_small_purple)
        small_purple_count += len(exclusive_small_purple)
   
    #etc...

# Calculate Tubes to be combined

   # SST_max = 4 #serum is only half of total volume
   # small_purple_max = 4
   # big_purple_max = 10
   # red_max = 3 #red tubes also collect serum
    
    pairable_SST = match[(match['Can Combine']!='N') & (match['Tube']=='SST')]
    if len(pairable_SST) > 0:
        SST_paired = pd.DataFrame()
        sorted_pairable_SST = pairable_SST.sort_values(by='Volume (ml)')
        #st.write(sorted_pairable_SST)
        while len(sorted_pairable_SST) > 1:
            
            # ~~~~~THIS NEXT LINE WILL NEED CHANGED WHEN REAL DATA IS IMPORTED ~~~~~
            # omg im a genius. thank christ I wrote that

            if sorted_pairable_SST.iloc[0,3]+sorted_pairable_SST.iloc[len(sorted_pairable_SST)-1,3] <= 4:
               # st.write(len(sorted_pairable_red))
              #  st.write('-2')
               # st.write(sorted_pairable_red.iloc[0,0])
               # st.write(sorted_pairable_red.iloc[len(sorted_pairable_red)-1,0])
                SST_paired = pd.concat([SST_paired,sorted_pairable_SST.iloc[[0]]], ignore_index=True)
                SST_paired = pd.concat([SST_paired,sorted_pairable_SST.iloc[[len(sorted_pairable_SST)-1]]], ignore_index=True)
                sorted_pairable_SST = sorted_pairable_SST.iloc[1:]
                sorted_pairable_SST = sorted_pairable_SST.iloc[:-1]
             #   st.write(len(sorted_pairable_red))
                SST_count += 1
            else:
             #   st.write(len(sorted_pairable_red))
             #   st.write('-1')
                exclusive_SST = pd.concat([exclusive_SST,sorted_pairable_SST.iloc[[len(sorted_pairable_SST)-1]]])
                sorted_pairable_SST = sorted_pairable_SST.iloc[:-1]
                SST_count += 1
        if len(sorted_pairable_SST) == 1:
           # st.write(len(sorted_pairable_red))
           # st.write('-1')
            exclusive_SST = pd.concat([exclusive_SST,sorted_pairable_SST.iloc[[len(sorted_pairable_SST)-1]]])
            sorted_pairable_SST = sorted_pairable_SST.iloc[:-1]
            SST_count += 1
        st.write(f"**Total SST Tubes:**", str(SST_count))

        ### Special Collection Instructions ###
################## DO THIS FOR ALL THE TUBES ###########
        SST_paired_notes = pd.DataFrame()
        SST_exclusive_notes = pd.DataFrame()
        if len(SST_paired) > 0:
            SST_paired_notes = SST_paired[SST_paired.iloc[:,5].notna()]
        if len(exclusive_SST) > 0:
            SST_exclusive_notes = exclusive_SST[exclusive_SST.iloc[:,5].notna()]
        if len(SST_paired_notes) > 0 or len(SST_exclusive_notes) > 0:
            with st.expander('SST Special collection notes: '):
                if len(SST_paired_notes) > 0:
                    k = 0
                    while k < len(SST_paired_notes):
                        st.write(f"**{SST_paired_notes.iloc[k,1]}**", ": ", SST_paired_notes.iloc[k,5])
                        k += 1
                if len(SST_exclusive_notes) > 0:
                    k = 0
                    while k < len(SST_exclusive_notes):
                        st.write(f"**{SST_exclusive_notes.iloc[k,1]}**", ": ", SST_exclusive_notes.iloc[k,5])
                        k += 1

        if show_details == True:
            if len(SST_paired) != 0:
                st.write('SST labs sharing tubes: ', SST_paired)
            if len(exclusive_SST) != 0:
                st.write('SST labs not sharing tubes: ', exclusive_SST)
    elif len(exclusive_SST) > 0:
        st.write(f"**Total SST Tubes:**", SST_count)
        if show_details == True:
            st.write('SST labs not sharing tubes: ', exclusive_SST)

        SST_exclusive_notes = exclusive_SST[(exclusive_SST.iloc[:,5].notna())]
        if len(SST_exclusive_notes) > 0:
            with st.expander('SST Special collection notes: '):
                k = 0
                while k < len(SST_exclusive_notes):
                    st.write(f"**{SST_exclusive_notes.iloc[k,1]}**", ": ", SST_exclusive_notes.iloc[k,5])
                    k += 1


    pairable_red = match[(match['Can Combine']!='N') & (match['Tube']=='Red')]
    if len(pairable_red) > 0:
        red_paired = pd.DataFrame()
        sorted_pairable_red = pairable_red.sort_values(by='Volume (ml)')
        #st.write(sorted_pairable_SST)
        while len(sorted_pairable_red) > 1:
            
            # ~~~~~THIS NEXT LINE WILL NEED CHANGED WHEN REAL DATA IS IMPORTED ~~~~~
            # omg im a genius. thank christ I wrote that

            if sorted_pairable_red.iloc[0,3]+sorted_pairable_red.iloc[len(sorted_pairable_red)-1,3] <= 3:
                #st.write(sorted_pairable_red)
               #  st.write('-2')
               # st.write(sorted_pairable_red.iloc[0,0]) 
               # st.write(sorted_pairable_red.iloc[len(sorted_pairable_red)-1,0])
                red_paired = pd.concat([red_paired,sorted_pairable_red.iloc[[0]]], ignore_index=True)
                red_paired = pd.concat([red_paired,sorted_pairable_red.iloc[[len(sorted_pairable_red)-1]]], ignore_index=True)
                sorted_pairable_red = sorted_pairable_red.iloc[1:]
                sorted_pairable_red = sorted_pairable_red.iloc[:-1]
                #st.write(len(sorted_pairable_red))
                red_count += 1
            else:
             #   st.write(len(sorted_pairable_red))
             #   st.write('-1')
                exclusive_red = pd.concat([exclusive_red,sorted_pairable_red.iloc[[len(sorted_pairable_red)-1]]])
                sorted_pairable_red = sorted_pairable_red.iloc[:-1]
                red_count += 1
        if len(sorted_pairable_red) == 1:
           # st.write(len(sorted_pairable_red))
           # st.write('-1')
            exclusive_red = pd.concat([exclusive_red,sorted_pairable_red.iloc[[len(sorted_pairable_red)-1]]])
            sorted_pairable_red = sorted_pairable_red.iloc[:-1]
            red_count += 1
        st.write(f"**Total Red Tubes:**", red_count)

        ### Special Collection Instructions ###
        red_paired_notes = pd.DataFrame()
        red_exclusive_notes = pd.DataFrame()
        if len(red_paired) > 0:
            red_paired_notes = red_paired[(red_paired.iloc[:,5].notna())]
        if len(exclusive_red) > 0:
            red_exclusive_notes = exclusive_red[exclusive_red.iloc[:,5].notna()]
        if len(red_paired_notes) > 0 or len(red_exclusive_notes) > 0:
            with st.expander('Red-Top Special collection notes: '):
                if len(red_paired_notes) > 0:
                    k = 0
                    while k < len(red_paired_notes):
                        st.write(f"**{red_paired_notes.iloc[k,1]}**", ": ", red_paired_notes.iloc[k,5])
                        k += 1
                if len(red_exclusive_notes) > 0:
                    k = 0
                    while k < len(red_exclusive_notes):
                        st.write(f"**{red_exclusive_notes.iloc[k,1]}**", ": ", red_exclusive_notes.iloc[k,5])
                        k += 1

        if show_details == True:
            if len(red_paired) != 0:    
                st.write('red labs sharing tubes:',red_paired)
            if len(exclusive_red) != 0:    
                st.write('red labs not sharing tubes:',exclusive_red)
    elif len(exclusive_red) > 0:
        st.write(f"**Total Red Tubes:**", red_count)

        red_exclusive_notes = exclusive_red[(exclusive_red.iloc[:,5].notna())]
        if len(red_exclusive_notes) > 0:
            with st.expander('Red-Top Special collection notes: '):
                k = 0
                while k < len(red_exclusive_notes):
                    st.write(f"**{red_exclusive_notes.iloc[k,1]}**", ": ", red_exclusive_notes.iloc[k,5])
                    k += 1


    if pair_purple == True:
        pairable_purple = match[(match['Can Combine']!='N') & (match['Tube']=='EDTA')]
      
        if len(pairable_purple) > 0:
            purple_paired = pd.DataFrame()
            sorted_pairable_purple = pairable_purple.sort_values(by='Volume (ml)')

            while len(sorted_pairable_purple) > 1:
            
            # ~~~~~THIS NEXT LINE WILL NEED CHANGED WHEN REAL DATA IS IMPORTED ~~~~~
            
                if sorted_pairable_purple.iloc[0,3]+sorted_pairable_purple.iloc[len(sorted_pairable_purple)-1,3] <= 4:
               # st.write(len(sorted_pairable_red))
              #  st.write('-2')
               # st.write(sorted_pairable_red.iloc[0,0])
               # st.write(sorted_pairable_red.iloc[len(sorted_pairable_red)-1,0])
                    purple_paired = pd.concat([purple_paired,sorted_pairable_purple.iloc[[0]]], ignore_index=True)
                    purple_paired = pd.concat([purple_paired,sorted_pairable_purple.iloc[[len(sorted_pairable_purple)-1]]], ignore_index=True)
                    sorted_pairable_purple = sorted_pairable_purple.iloc[1:]
                    sorted_pairable_purple = sorted_pairable_purple.iloc[:-1]
             #   st.write(len(sorted_pairable_red))
                    small_purple_count += 1
                elif sorted_pairable_purple.iloc[0,3]+sorted_pairable_purple.iloc[len(sorted_pairable_purple)-1,3] <= 10:
                    purple_paired = pd.concat([purple_paired,sorted_pairable_purple.iloc[[0]]], ignore_index=True)
                    purple_paired = pd.concat([purple_paired,sorted_pairable_purple.iloc[[len(sorted_pairable_purple)-1]]], ignore_index=True)
                    sorted_pairable_purple = sorted_pairable_purple.iloc[1:]
                    sorted_pairable_purple = sorted_pairable_purple.iloc[:-1]
             #   st.write(len(sorted_pairable_red))
                    big_purple_count += 1
                
                else:
                 #   st.write(len(sorted_pairable_red))
                 #   st.write('-1')
                    exclusive_big_purple = pd.concat([exclusive_big_purple,sorted_pairable_purple.iloc[[len(sorted_pairable_purple)-1]]])
                    sorted_pairable_purple = sorted_pairable_purple.iloc[:-1]
                    big_purple_count += 1
            if len(sorted_pairable_purple) == 1:
           # st.write(len(sorted_pairable_red))
           # st.write('-1')
                if sorted_pairable_purple.iloc[0,3] <= 4:
                    exclusive_small_purple = pd.concat([exclusive_small_purple,sorted_pairable_purple.iloc[[len(sorted_pairable_purple)-1]]])
                    sorted_pairable_purple = sorted_pairable_purple.iloc[:-1]
                    small_purple_count += 1
                else:
                    exclusive_big_purple = pd.concat([exclusive_big_purple,sorted_pairable_purple.iloc[[len(sorted_pairable_purple)-1]]])
                    sorted_pairable_purple = sorted_pairable_purple.iloc[:-1]
                    big_purple_count += 1

            st.write(f"**Total Big Purple Tubes:**", big_purple_count)
            st.write(f"**Total Small Purple Tubes:**", small_purple_count)
            if show_details == True:
                if len(purple_paired) != 0:
                    st.write('EDTA labs sharing a tube: ', purple_paired)
                if len(exclusive_big_purple) != 0:
                    st.write('EDTA labs alone in a big purple: ', exclusive_big_purple)
                if len(exclusive_small_purple) != 0:
                    st.write('EDTA labs alone in a small purple: ', exclusive_small_purple)
            
        ### Special Collection Instructions ###
        purple_paired_notes = pd.DataFrame()
        purple_exclusive_notes = pd.DataFrame()
        purple_paired_notes = purple_paired[purple_paired.iloc[:,5].notna()]
        purple_exclusive_notes = pd.concat([exclusive_small_purple[exclusive_small_purple.iloc[:,5].notna()], exclusive_big_purple[exclusive_big_purple.iloc[:,5].notna()]])
        if len(purple_paired_notes) > 0 or len(purple_exclusive_notes) > 0:
            with st.expander('EDTA Special collection notes: '):
                if len(purple_paired_notes) > 0:
                    k = 0
                    while k < len(purple_paired_notes):
                        st.write(f"**{purple_paired_notes.iloc[k,1]}**", ": ", purple_paired_notes.iloc[k,5])
                        k += 1
                if len(purple_exclusive_notes) > 0:
                    k = 0
                    while k < len(purple_exclusive_notes):
                        st.write(f"**{purple_exclusive_notes.iloc[k,1]}**", ": ", purple_exclusive_notes.iloc[k,5])
                        k += 1
    else:
        if big_purple_count > 0:
            st.write(f"**Total Big Purple Tubes:**", big_purple_count)
            if show_details == True:
                st.write(exclusive_big_purple)
        if small_purple_count > 0:
            st.write(f"**Total Small Purple Tubes:**", small_purple_count)
            if show_details == True:    
                st.write(exclusive_small_purple)
        purple_exclusive_notes = pd.concat([exclusive_small_purple[exclusive_small_purple.iloc[:,5].notna()], exclusive_big_purple[exclusive_big_purple.iloc[:,5].notna()]])
        if len(purple_exclusive_notes) > 0:
                    with st.expander('EDTA Special collection notes: '):
                        k = 0
                        while k < len(purple_exclusive_notes):
                            st.write(f"**{purple_exclusive_notes.iloc[k,1]}**", ": ", purple_exclusive_notes.iloc[k,5])
                            k += 1

    other_labs = match[(match['Tube']!='EDTA') & (match['Tube']!='SST') & (match['Tube']!='Red')]
    if len(other_labs) > 0:
        st.subheader('Other labs: ')
        j = 0
        while j < len(other_labs['Tube'].unique()):
            st.write('Lab Type: ',other_labs['Tube'].unique()[j])
            st.write(other_labs[(other_labs['Tube']==other_labs['Tube'].unique()[j])])
            j += 1
if show_details == True:
    full_list = st.checkbox('Need more details? Click here to show the full directory')
    if full_list == True:
        st.write(df)
st.divider()
st.write("Find something that doesn't look correct? Email Kate at katherinedubovi@centraloutreach.com.")
st.write("Data used for this program was acquired from the Quest Diagnostics Test Directory. In an abundence of caution, labs use preferred specimen size rather than minimum specimen size. In some cases, a smaller specimen is acceptable.")
