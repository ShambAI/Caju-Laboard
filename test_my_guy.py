from grobid_client.grobid_client import GrobidClient
from concurrent.futures import ProcessPoolExecutor

h = "/mnt/c/Users/Dami Olawoyin-Yussuf/Documents/Power_for_all_project/peak-oss_/peak-oss/"

def run_grobid():
    client = GrobidClient(config_path= "grobid_config.json")
    client.process("processFulltextDocument",
                   h + "data/docs/copied_base_file",
                   output= h + "data/docs/converted_xml",
                   consolidate_citations=True,
                   teiCoordinates=True,
                   force=True
                   )

    return "grobid reached here"

if __name__ == "__main__":

    run_grobid()
    
    # futures = []
    # with ProcessPoolExecutor() as executor:
    #     futures.append(executor.submit(run_grobid,))

    #     for future in futures:
    #         print(future.result())