import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


# ritorna la lista delle economie
def get_lista_economie(df):
    lista_economie = []
    lower_bound = 0
    upper_bound = 0
    in_economia = False
    for row in df.itertuples():
        if row.econ == False and in_economia == False:
            in_economia = False
        if row.econ == False and in_economia == True:
            in_economia = False
            previous_row = df.loc[getattr(row, "Index") - 1]
            upper_bound = previous_row.compact_course
            x = {"min": lower_bound, "max": upper_bound}
            lista_economie.append(x)
        if row.econ == True and in_economia == False:
            in_economia = True
            lower_bound = row.compact_course
    return lista_economie


# ritorna la lista delle zone della calza con il relativo colore associato
def get_lista_zone(df):
    cmap = matplotlib.cm.get_cmap('tab20')
    df = df.reset_index(drop=True)
    lista_zone = []
    lower_bound = 0
    upper_bound = 0
    first_row = True
    actual_zone = ""
    last_row = False
    contatore = 0
    for row in df.itertuples():
        last_row = (getattr(row, "Index") == len(df) - 1)
        if first_row:
            actual_zone = row.zone
            lower_bound = 0
            first_row = False
        if row.zone != actual_zone:
            previous_row = df.loc[getattr(row, "Index") - 1]
            upper_bound = row.compact_course
            x = {"min": lower_bound, "max": upper_bound, "zone": actual_zone,
                 "color": matplotlib.colors.to_hex(cmap.colors[contatore])}
            actual_zone = row.zone
            lista_zone.append(x)
            lower_bound = row.compact_course
            contatore += 1
        if last_row:
            upper_bound = row.compact_course
            x = {"min": lower_bound, "max": upper_bound, "zone": actual_zone,
                 "color": matplotlib.colors.to_hex(cmap.colors[contatore])}
            lista_zone.append(x)
    return lista_zone


# dato il df_artocde_ e il df_errors_plus ritorna un df_errors_plus con l'aggiunta del rango
def add_rango_to_errors_plus(df_errors, df_art, df_references, program_name):
    # dato un programma e il df_artcode_references ritorna l'hash più utilizzato di tale programma
    df_references = df_references[df_references["program_name"] == program_name]
    most_common_hash = df_references.groupby(["hash"])["hash"].count().sort_values(ascending=False).index[0]
    #
    df_art = df_art.loc[df_art["hash"] == most_common_hash]
    df_errors = df_errors.loc[df_errors["program"] == program_name]
    df_errors["rango"] = np.nan
    for row in df_errors.itertuples():
        # se lo step non è in un economia allora prendo il corrispettivo rango
        # riga/righe di df_artcode con step = step di errors_plus
        row_artcode = df_art.loc[df_art["step"] == row.step]
        if len(row_artcode) == 1:
            # caso di corrispondenza step-rango
            # il rango di df_errors_plus è uguale al rango di df_artcode in cui lo step è uguale
            row_index = getattr(row, 'Index')
            df_errors.loc[row_index, "rango"] = row_artcode["compact_course"].values[0]
        elif len(row_artcode) > 1 and all(row_artcode["econ"]):
            # Sono in un economia. le righe di df_artcode corrsipondenti sono più di una e tutte tali righe hanno il
            # valore di econ=True prendo il primo rango dell'economia
            primo_rango_economia = row_artcode["compact_course"].values[0]
            rango_effettivo = primo_rango_economia + row.course
            row_index = getattr(row, 'Index')
            df_errors.loc[row_index, "rango"] = rango_effettivo
        elif len(row_artcode) == 0:
            # se non trovo delle corrispondenze tra lo step di errors_plus e df_artcode assegno l'ultimo rango di df_artcode.
            # potrebbe essere che in df_errors_plus ho rango=127 mentre il rango max di df_artocde è 126, questo è dovuto
            # al fatto che sto considernado un artcode con qualche passo di economia in meno. in questo caso prendo come
            # rango effettivo il rango massimo dell'artcode.
            row_index = getattr(row, 'Index')
            df_errors.loc[row_index, "rango"] = df_art.iloc[-1]["compact_course"]
    df_errors["rango"].astype("int")
    # rimuovi rango 0 da df_errors e mettilo in un df separato
    df_errors_rango_zero = df_errors[df_errors.rango == 0]
    df_errors = df_errors.drop(df_errors[df_errors.rango == 0].index)
    return df_errors, df_errors_rango_zero, df_art


def get_programs_list():
    df_artcode_references = pd.read_csv("references.csv")
    programs_list = list(set(df_artcode_references["program_name"]))
    programs_list = sorted(programs_list)
    return programs_list


def get_machines_list():
    df_artcode_references = pd.read_csv("references.csv")
    machines_list = list(set(df_artcode_references["machine_id"]))
    machines_list = sorted(machines_list)
    return machines_list


# df_artcode = pd.read_csv("artcode.csv")
# df_errors_plus = pd.read_csv("errors_plus.csv")
# df_artcode_references = pd.read_csv("references.csv")
def get_df_errors_plus(df_errors_plus, discard_check, program, family, macchina):
    df_errors_plus = df_errors_plus[df_errors_plus["program"] == program]
    if family is not None:
        df_errors_plus = df_errors_plus[df_errors_plus["family"] == family]
    if macchina is not None:
        df_errors_plus = df_errors_plus[df_errors_plus["machine_id"] == macchina]
    if discard_check == "True":
        df_errors_plus = df_errors_plus[df_errors_plus["discard"] == True]
    if discard_check == "False":
        df_errors_plus = df_errors_plus[df_errors_plus["discard"] != True]
    return df_errors_plus


def get_df_artcode():
    df_artcode = pd.read_csv("artcode.csv")
    return df_artcode


def get_df_artcode_references():
    df_artcode_references = pd.read_csv("references.csv")
    return df_artcode_references


def get_top_10_family_code(df_errors_plus):
    df = (df_errors_plus.groupby("family_code")["family_code"].count()
          .reset_index(name='count')
          .sort_values(("count"), ascending=False)
          .head(10)
          )
    lista_top_10_family_code = df["family_code"].tolist()
    return lista_top_10_family_code


def get_top_10_family_code_and_count(df_errors_plus):
    df = (df_errors_plus.groupby("family_code")["family_code"].count()
          .reset_index(name='count')
          .sort_values(("count"), ascending=False)
          .head(10)
          )
    top_10_family_code_and_count = df[["family_code","count"]]
    return top_10_family_code_and_count

def get_errors_per_rango_e_family_code(df_errors_plus):
    lista_top_10_family_code = get_top_10_family_code(df_errors_plus)
    df_errors = df_errors_plus[df_errors_plus["family_code"].isin(lista_top_10_family_code)]
    df = (df_errors.groupby(['rango', 'family_code'])["family_code"].count()
          .reset_index(name='count')
          .sort_values(['rango', 'count'], ascending=[True, False])
          )
    df = df.reset_index(drop=True)
    return df


def get_map_codici(df_errors_plus):
    lista_top_10_family_code = get_top_10_family_code(df_errors_plus)
    dict_codici = {}
    cmap = matplotlib.cm.get_cmap('tab10')
    for i in range(1, 11):
        dict_codici[lista_top_10_family_code[i - 1]] = matplotlib.colors.rgb2hex(cmap(i))
    return dict_codici
