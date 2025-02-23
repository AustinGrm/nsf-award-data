import os
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from lxml import etree
import logging
from datetime import datetime
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_to_db():
    """Create database connection"""
    return psycopg2.connect(
        dbname="nsf",
        user="austinavent",  # Replace with your computer's username
        password="",  # Add if needed
        host="localhost"
    )

def parse_xml_to_dict(xml_file):
    """Parse single XML file to dictionary"""
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
        award = root.find('.//Award')
        
        # Extract data with safe navigation
        def safe_text(element_path):
            element = award.find(element_path)
            return element.text if element is not None else None
        
        return {
            'award_id': safe_text('.//AwardID'),
            'award_title': safe_text('.//AwardTitle'),
            'agency': safe_text('.//AGENCY'),
            'award_effective_date': safe_text('.//AwardEffectiveDate'),
            'award_expiration_date': safe_text('.//AwardExpirationDate'),
            'award_total_intn_amount': safe_text('.//AwardTotalIntnAmount'),
            'award_amount': safe_text('.//AwardAmount'),
            'award_instrument_value': safe_text('.//AwardInstrument/Value'),
            'org_directorate_abbr': safe_text('.//Organization/Directorate/Abbreviation'),
            'org_directorate_name': safe_text('.//Organization/Directorate/LongName'),
            'org_division_abbr': safe_text('.//Organization/Division/Abbreviation'),
            'org_division_name': safe_text('.//Organization/Division/LongName'),
            'pi_first_name': safe_text('.//Investigator/FirstName'),
            'pi_last_name': safe_text('.//Investigator/LastName'),
            'pi_email': safe_text('.//Investigator/EmailAddress'),
            'institution_name': safe_text('.//Institution/Name'),
            'institution_city': safe_text('.//Institution/CityName'),
            'institution_state': safe_text('.//Institution/StateCode'),
            'abstract_narration': safe_text('.//AbstractNarration'),
            'raw_xml': etree.tostring(award, encoding='unicode')
        }
    except Exception as e:
        logging.error(f"Error parsing {xml_file}: {str(e)}")
        return None

def bulk_insert_awards(conn, awards_data):
    """Bulk insert awards into database"""
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO raw_awards (
        award_id, award_title, agency, award_effective_date, award_expiration_date,
        award_total_intn_amount, award_amount, award_instrument_value,
        org_directorate_abbr, org_directorate_name, org_division_abbr, org_division_name,
        pi_first_name, pi_last_name, pi_email,
        institution_name, institution_city, institution_state,
        abstract_narration, raw_xml
    ) VALUES %s
    """
    
    # Convert data to tuples for bulk insert
    values = [(
        d['award_id'], d['award_title'], d['agency'],
        d['award_effective_date'], d['award_expiration_date'],
        d['award_total_intn_amount'], d['award_amount'],
        d['award_instrument_value'],
        d['org_directorate_abbr'], d['org_directorate_name'],
        d['org_division_abbr'], d['org_division_name'],
        d['pi_first_name'], d['pi_last_name'], d['pi_email'],
        d['institution_name'], d['institution_city'], d['institution_state'],
        d['abstract_narration'], d['raw_xml']
    ) for d in awards_data]
    
    execute_values(cursor, insert_query, values)
    conn.commit()

def process_xml_files(directory, batch_size=1000):
    """Process all XML files in directory with batching"""
    # Debug: Print absolute path
    abs_path = os.path.abspath(directory)
    logging.info(f"Looking for XML files in: {abs_path}")
    
    # List files before processing
    xml_files = list(Path(directory).rglob('*.xml'))
    logging.info(f"Found {len(xml_files)} XML files")
    
    # Debug: Print first few file paths if any exist
    if xml_files:
        logging.info("First few files found:")
        for f in xml_files[:3]:
            logging.info(f"  {f}")
    else:
        logging.error("No XML files found! Check directory path.")
        return

    conn = connect_to_db()
    current_batch = []
    total_processed = 0
    
    # Get total file count for progress bar
    total_files = len(xml_files)
    
    with tqdm(total=total_files, desc="Processing XML files") as pbar:
        for xml_file in xml_files:
            award_data = parse_xml_to_dict(xml_file)
            if award_data:
                current_batch.append(award_data)
                
                if len(current_batch) >= batch_size:
                    bulk_insert_awards(conn, current_batch)
                    total_processed += len(current_batch)
                    current_batch = []
            
            pbar.update(1)
        
        # Insert any remaining records
        if current_batch:
            bulk_insert_awards(conn, current_batch)
            total_processed += len(current_batch)
    
    conn.close()
    logging.info(f"Total records processed: {total_processed}")

if __name__ == "__main__":
    start_time = datetime.now()
    process_xml_files('randys_data')  # or whatever your directory is named
    end_time = datetime.now()
    logging.info(f"Total processing time: {end_time - start_time}")