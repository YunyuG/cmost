from dataclasses import dataclass,field
import streamlit as st
import asyncio
import cmost as cst
from pathlib import Path
from utils import clean_cache

clean_cache()

@dataclass
class UserSubmitInfo:
    dr_number: str
    TOKEN: str
    obsid_list:list = field(repr=False)
    is_med:bool
    save_dir:str

    def __post_init__(self):
        self.obsid_list = [int(i.strip()) for i in self.obsid_list.strip().split("\n")] if self.obsid_list is not None else None


def start_download(u:UserSubmitInfo):
    dr_number: str = u.dr_number
    TOKEN: str = u.TOKEN
    obsid_list:list = u.obsid_list
    is_med:bool = u.is_med
    save_dir:str = u.save_dir

    if isinstance(obsid_list,int):
        obsid_list = [obsid_list]

    if save_dir == "":
        save_dir = "fits"
        Path("fits").mkdir(exist_ok=True)
    elif save_dir=="./":
        pass
    else:
        Path(save_dir).mkdir(exist_ok=True)
    
    cst.download_fits(obsids_list=obsid_list
                        ,dr_number=dr_number
                        ,TOKEN=TOKEN
                        ,is_med=is_med
                        ,save_dir=save_dir)

    
    # with st.spinner("Downloading..."):
    #     pass
            
            
st.set_page_config(page_title="CMOST GUI"
                   ,page_icon=str(Path(__file__).parent/"assets/ico.png")
                   ,layout="centered",
                   initial_sidebar_state="auto"
                   )

c1,c2 = st.columns([1.5,1])
with c1:
    st.header("Download of LAMOST Spectral Data",divider="gray")
    # st.text

with c2:
    st.image(str(Path(__file__).parent/"assets/download.jpg"),width=300)

with st.form("my_form"):
    u = UserSubmitInfo(
        dr_number=st.number_input("please input dr number：",value=13,min_value=1,max_value=13)
        ,TOKEN=st.text_input("*if datasets of this version are not open, please input token：",value=None)
        ,obsid_list=st.text_area("please input obsid",value=None)
        ,is_med=st.toggle("If you need to download files of medium-resolution spectra, please turn on this switch.")
        ,save_dir=st.text_input("please input save dir：",value="")
    )
    submit_bit = st.form_submit_button("Submit")
    if submit_bit:
        try:
        # gui_print(u)
            if u.obsid_list is None:
                st.error("obsid_list should not be None")
                st.stop()
            if u.dr_number is None:
                st.error("dr_number should not be None")
                st.stop()
            start_download(u)
        except Exception as e:
            st.error("It is possible that the parameters you entered are incorrect, or the dataset of this version is not open." \
            " Please try entering the TOKEN or check your network and parameters.")
            st.exception(e)