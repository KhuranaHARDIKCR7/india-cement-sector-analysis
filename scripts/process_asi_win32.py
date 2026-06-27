import os
import glob
import shutil
import pandas as pd
import numpy as np
import win32com.client

# Base directory setup
base_dir = os.path.dirname(os.path.abspath(__file__))
out_dir_base = os.path.join(base_dir, "data", "processed")

# Years definition
years_to_process = [
    ('2009_10', '200910'),
    ('2010_11', '201011'),
    ('2011_12', '201112'),
    ('2012_13', '201213'),
    ('2013_14', '201314')
]

# Rename mapping for Block A
a_rename_maps = {
    '2009_10': {
        'YR': 'Year', 'A_Itm2': 'PSL', 'A_Itm3': 'Scheme', 'A_Itm4': 'INC4digit',
        'A_Itm5': 'INC5digit', 'A_Itm7': 'State', 'A_Itm8': 'District', 'A_Itm9': 'Rural_Urban',
        'A_Itm10': 'RO_SRO', 'A_Itm11': 'Unit', 'A_Itm12': 'Status_Unit', 'E_Itm10': 'Bonus',
        'E_Itm11': 'ProvidentFund', 'E_Itm12': 'Welfare', 'E_Itm13a': 'MWorkingdays',
        'E_Itm13b': 'NMWorkingdays', 'E_Itm13c': 'TWorkingdays', 'E_Itm14': 'CostofProd',
        'J_Itm13': 'Share', 'WGT': 'Multilplier'
    },
    'default': {
        'NIC4digit': 'INC4digit', 'NIC5digit': 'INC5digit', 'StateCode': 'State',
        'NoofUnits': 'Unit', 'Statusofunit': 'Status_Unit'
    }
}

# Rename mapping for blocks
block_mappings = {
    'h': {
        '2009_10': {
            'YR': 'Year', 'BLK': 'BLK', 'DSL': 'DSL', 'H_Itm1': 'Sno',
            'H_Itm3': 'ItemCode', 'H_Itm4': 'Unitcode', 'H_Itm5': 'QtyCons', 'H_Itm6': 'PurVal'
        },
        'default': {
            'DSL': 'DSL', 'Sno': 'Sno', 'ItemCode': 'ItemCode', 'Unitcode': 'Unitcode',
            'QtyCons': 'QtyCons', 'PurVal': 'PurVal'
        }
    },
    'i': {
        '2009_10': {
            'YR': 'Year', 'BLK': 'BLK', 'DSL': 'DSL', 'I_Itm1': 'Sno',
            'I_Itm3': 'ItemCode', 'I_Itm4': 'Unitcode', 'I_Itm5': 'QtyCons', 'I_Itm6': 'Purvaldel',
            'I_Itm7': 'Rateperunit'
        },
        'default': {
            'DSL': 'DSL', 'Sno': 'Sno', 'ItemCode': 'ItemCode', 'Unitcode': 'Unitcode',
            'QtyCons': 'QtyCons', 'Purvaldel': 'Purvaldel', 'Rateperunit': 'Rateperunit'
        }
    },
    'j': {
        '2009_10': {
            'YR': 'Year', 'BLK': 'BLK', 'DSL': 'DSL', 'J_Itm1': 'Sno',
            'J_Itm3': 'ItemCode', 'J_Itm4': 'Unitcode', 'J_Itm5': 'QtyCons', 'J_Itm6': 'QtySold',
            'J_Itm7': 'Grosssalval', 'J_Itm8': 'ExciseDuty', 'J_Itm9': 'SalesTax', 'J_Itm10': 'Others',
            'J_Itm11': 'Total', 'J_Itm12': 'NetSaleval', 'J_Itm13': 'ExfactvalOutput'
        },
        'default': {
            'DSL': 'DSL', 'Sno': 'Sno', 'ItemCode': 'ItemCode', 'Unitcode': 'Unitcode',
            'QtyManuf': 'QtyCons', 'QtySold': 'QtySold', 'Grosssalval': 'Grosssalval',
            'ExciseDuty': 'ExciseDuty', 'SalesTax': 'SalesTax', 'Others': 'Others',
            'Total': 'Total', 'NetSaleval': 'NetSaleval', 'ExfactvalOutput': 'ExfactvalOutput'
        }
    }
}

# Unit maps / states are preserved in the templates, so we don't need to rebuild Sheet1.

def prepare_blka(year_folder, year_sfx):
    folder_path = os.path.join(base_dir, "data", "raw", f"ASI_DATA_{year_folder}_CSV")
    out_folder = os.path.join(out_dir_base, f"ASI_DATA_{year_folder}_CSV")
    os.makedirs(out_folder, exist_ok=True)
    
    if year_folder == '2009_10':
        blka_files = glob.glob(os.path.join(folder_path, "A-IDENTIFICATION*.csv"))
    else:
        blka_files = glob.glob(os.path.join(folder_path, "blka*.csv"))
        if not blka_files:
            blka_files = glob.glob(os.path.join(folder_path, "blkA*.csv"))
            
    df_a = pd.read_csv(blka_files[0], encoding='utf-8', low_memory=False)
    
    if year_folder == '2009_10':
        df_a.rename(columns=a_rename_maps['2009_10'], inplace=True)
    else:
        df_a.rename(columns=a_rename_maps['default'], inplace=True)
        
    dsl_col = [c for c in df_a.columns if 'DSL' in c.upper()][0]
    df_a[dsl_col] = pd.to_numeric(df_a[dsl_col], errors='coerce')
    
    out_blka = os.path.join(out_folder, f"blka{year_sfx}.xlsx")
    with pd.ExcelWriter(out_blka, engine='openpyxl') as writer:
        df_a.to_excel(writer, sheet_name=f'blka{year_sfx}', index=False)
    print(f"Prepared Block A for {year_folder} at {out_blka}")

def replicate_block(year_folder, year_sfx, block_char):
    block_lower = block_char.lower()
    folder_path = os.path.join(base_dir, "data", "raw", f"ASI_DATA_{year_folder}_CSV")
    out_folder = os.path.join(out_dir_base, f"ASI_DATA_{year_folder}_CSV")
    
    # 1. Find CSV file
    if year_folder == '2009_10':
        prefix = {'h': 'H-INPUT', 'i': 'I-INPUT', 'j': 'J-PRODUCTS'}[block_lower]
        csv_files = glob.glob(os.path.join(folder_path, f"{prefix}*.csv"))
    else:
        csv_files = glob.glob(os.path.join(folder_path, f"blk{block_char}*.csv"))
        if not csv_files:
            csv_files = glob.glob(os.path.join(folder_path, f"blk{block_char.upper()}*.csv"))
            
    if not csv_files:
        print(f"No CSV found for {year_folder} Block {block_char}")
        return
        
    # Read raw CSV
    df = pd.read_csv(csv_files[0], encoding='utf-8', low_memory=False)
    
    # Rename columns to match the target standard
    map_key = '2009_10' if year_folder == '2009_10' else 'default'
    df.rename(columns=block_mappings[block_lower][map_key], inplace=True)
    
    # Copy template
    ref_name = f"blk{block_lower}201415.xlsx"
    if block_lower == 'h': ref_name = 'blkH201415.xlsx'
    elif block_lower == 'i': ref_name = 'blkI201415.xlsx'
    
    ref_path = os.path.join(out_dir_base, "ASI_DATA_2014_15_CSV", ref_name)
    dest_path = os.path.join(out_folder, f"blk{block_lower}{year_sfx}.xlsx")
    
    shutil.copy(ref_path, dest_path)
    print(f"Copied template to {dest_path}")
    
    # Open dest_path in Excel via COM
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    
    wb = excel.Workbooks.Open(os.path.abspath(dest_path))
    try:
        sheet_ref_name = f"blk{block_lower}201415"
        if block_lower == 'h': sheet_ref_name = 'blkh201415'
        elif block_lower == 'i': sheet_ref_name = 'blkI201415'
        
        sheet = wb.Sheets(sheet_ref_name)
        sheet.Name = f"blk{block_lower}{year_sfx}"
        
        # Get old last row
        old_last_row = sheet.UsedRange.Rows.Count
        new_last_row = len(df) + 1  # 1-indexed, +1 for header
        
        # Clean extra rows first if old sheet was larger
        if old_last_row > new_last_row:
            sheet.Rows(f"{new_last_row+1}:{old_last_row}").Delete()
            
        # Write new raw data using 2D arrays
        # Block H columns mapping:
        # A: Year, B: BLK, C: DSL (AH01), F: HI1, G: NPCMS Item Code (HI3), I: Qty unit (HI4), L: Qty (HI5), N: Value (HI6)
        if block_lower == 'h':
            raw_cols = {
                'A': df['Year'].values,
                'B': df['BLK'].values,
                'C': df['DSL'].values,
                'F': df['Sno'].values,
                'G': df['ItemCode'].values,
                'I': df['Unitcode'].values,
                'L': df['QtyCons'].values,
                'N': df['PurVal'].values
            }
            formula_cols = ['D', 'E', 'H', 'J', 'K', 'M']
        
        # Block I columns mapping:
        # A: Year, B: BLK, C: DSL(AI01), D: II1, G: NPCMS(II3), I: II4, K: Qty(II5), M: Value (II6), O: Rateperunit
        elif block_lower == 'i':
            raw_cols = {
                'A': df['Year'].values,
                'B': df['BLK'].values,
                'C': df['DSL'].values,
                'D': df['Sno'].values,
                'G': df['ItemCode'].values,
                'I': df['Unitcode'].values,
                'K': df['QtyCons'].values,
                'M': df['Purvaldel'].values,
                'O': df['Rateperunit'].values
            }
            formula_cols = ['E', 'F', 'H', 'J', 'L', 'N']
            
        # Block J columns mapping:
        # A: Year, B: BLK, C: DSL (AJ01), D: J11, G: NPCMS (J13), I: Qty Unit (J14), L: Qty (J15), N: Qtysold, O: Grosssalval, P: Exciseduty, Q: Salestax, R: Others, S: Total, T: Netsaleval, U: ExfactvalOutput
        elif block_lower == 'j':
            raw_cols = {
                'A': df['Year'].values,
                'B': df['BLK'].values,
                'C': df['DSL'].values,
                'D': df['Sno'].values,
                'G': df['ItemCode'].values,
                'I': df['Unitcode'].values,
                'L': df['QtyCons'].values, # QtyManuf/QtyCons depending on mappings
                'N': df['QtySold'].values,
                'O': df['Grosssalval'].values,
                'P': df['ExciseDuty'].values,
                'Q': df['SalesTax'].values,
                'R': df['Others'].values,
                'S': df['Total'].values,
                'T': df['NetSaleval'].values,
                'U': df['ExfactvalOutput'].values
            }
            formula_cols = ['E', 'F', 'H', 'J', 'K', 'M']
            
        # Write raw columns
        for col_letter, values in raw_cols.items():
            # Convert values to 2D list
            val_list = [[v] for v in values]
            # Replace NaNs with empty string
            val_list = [['' if pd.isna(v) or v is None else v] for [v] in val_list]
            sheet.Range(f"{col_letter}2:{col_letter}{new_last_row}").Value = val_list
            
        # Replace external link reference in row 2 formulas
        # Point them from 2014_15_CSV\\[blka201415.xlsx]blka201415 to current year's blka
        old_ref = "2014_15_CSV\\[blka201415.xlsx]blka201415"
        new_ref = f"[blka{year_sfx}.xlsx]blka{year_sfx}"
        sheet.Cells.Replace(old_ref, new_ref)
        
        # AutoFill formulas
        for col_letter in formula_cols:
            source_range = sheet.Range(f"{col_letter}2")
            fill_range = sheet.Range(f"{col_letter}2:{col_letter}{new_last_row}")
            source_range.AutoFill(fill_range)
            
        # Update Pivot Table
        pivots = sheet.PivotTables()
        if pivots.Count > 0:
            pt = pivots.Item(1)
            # Find the number of columns in the raw data (usually N=14 for H, O=15 for I, U=21 for J)
            num_cols = {'h': 16, 'i': 15, 'j': 21}[block_lower] # using same as reference
            pt.SourceData = f"blk{block_lower}{year_sfx}!R1C1:R{new_last_row}C{num_cols}"
            pt.PivotCache().Refresh()
            print(f"Refreshed Pivot Table for Block {block_char} ({year_folder})")
            
        wb.Save()
        print(f"Successfully processed Block {block_char} for {year_folder}")
    finally:
        wb.Close(True)
        excel.Quit()

if __name__ == "__main__":
    for y_folder, y_sfx in years_to_process:
        print(f"=== Processing Year {y_folder} ===")
        prepare_blka(y_folder, y_sfx)
        for b in ['h', 'i', 'j']:
            replicate_block(y_folder, y_sfx, b)
