I use brew to install PostgreSQL. You may need different commands depending on your package manager.
This is done in terminal, but I recommend you first download warp. Its a terminal app that makes it easier to use terminal commands with AI. IMO, no reason to do anything the hard way.

# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb nsf

# Create and activate virtual environment
python -m venv nsf
source nsf/bin/activate

# Install required packages
pip install psycopg2-binary lxml tqdm

# Connect to database
psql nsf

# Create the table (paste this into psql)
CREATE TABLE raw_awards (
    id SERIAL PRIMARY KEY,
    award_id VARCHAR(10),
    award_title TEXT,
    agency VARCHAR(10),
    award_effective_date DATE,
    award_expiration_date DATE,
    award_total_intn_amount DECIMAL(15,2),
    award_amount DECIMAL(15,2),
    award_instrument_value VARCHAR(100),
    org_directorate_abbr VARCHAR(10),
    org_directorate_name TEXT,
    org_division_abbr VARCHAR(10),
    org_division_name TEXT,
    pi_first_name VARCHAR(100),
    pi_last_name VARCHAR(100),
    pi_email TEXT,
    institution_name TEXT,
    institution_city VARCHAR(100),
    institution_state VARCHAR(2),
    abstract_narration TEXT,
    raw_xml TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Edit the database connection in data_insertion.py
# Change this line to match your username:
    dbname="nsf",
    user="your_username",  # Your Mac username
    password="",          # Leave blank if no password set
    host="localhost"

# Run the script
python data_insertion.py

psql nsf
=> SELECT COUNT(*) FROM raw_awards;

# Here is a more complex query that shows top orgs and institutions by funding

-- Basic count of awards
SELECT COUNT(*) as total_awards FROM raw_awards;

-- Distribution of awards by directorate with total funding
SELECT 
    org_directorate_name,
    COUNT(*) as award_count,
    SUM(award_amount::numeric) as total_funding,
    AVG(award_amount::numeric) as avg_award
FROM raw_awards
GROUP BY org_directorate_name
ORDER BY total_funding DESC;

-- Top 10 institutions by funding
SELECT 
    institution_name,
    institution_state,
    COUNT(*) as num_awards,
    SUM(award_amount::numeric) as total_funding
FROM raw_awards
GROUP BY institution_name, institution_state
ORDER BY total_funding DESC
LIMIT 10;


# Here is the result:
        ^
             org_directorate_name              | award_count | total_funding |      avg_award      
-----------------------------------------------+-------------+---------------+---------------------
 Directorate For Geosciences                   |        1838 | 1809966855.00 | 984748.016866158868
 Direct For Mathematical & Physical Scien      |        2635 | 1516390229.00 | 575480.162808349146
 Direct For Biological Sciences                |        1505 |  807614272.00 | 536620.778737541528
 Directorate For Engineering                   |        1821 |  689506421.00 | 378641.637012630423
 Direct For Education and Human Resources      |         644 |  601869574.00 | 934580.083850931677
 Direct For Computer & Info Scie & Enginr      |        1605 |  597206702.00 | 372091.403115264798
 Directorate for STEM Education                |         581 |  540958671.00 | 931082.049913941480
 Direct For Social, Behav & Economic Scie      |        1218 |  334646068.00 | 274750.466338259442
 Office Of The Director                        |         429 |  149249592.00 | 347901.146853146853
 Dir for Tech, Innovation, & Partnerships      |         308 |  103457646.00 | 335901.448051948052
                                               |          10 |    2232094.00 | 223209.400000000000
 Office of Budget, Finance, & Award Management |          10 |     980514.00 |  98051.400000000000
 National Coordination Office                  |           1 |     919100.00 | 919100.000000000000
 Office Of Information & Resource Mgmt         |           7 |     604667.00 |  86381.000000000000
(14 rows)

              institution_name              | institution_state | num_awards | total_funding 
--------------------------------------------+-------------------+------------+---------------
 University Corporation For Atmospheric Res | CO                |         21 | 1104988786.00
 California Institute of Technology         | CA                |         59 |  276740397.00
 University of Washington                   | WA                |        211 |  111565059.00
 University of Wisconsin-Madison            | WI                |        165 |  107065963.00
 Cornell University                         | NY                |        122 |  101302902.00
 University of Illinois at Urbana-Champaign | IL                |        199 |   95320337.00
 University of California-Berkeley          | CA                |        182 |   88496594.00
 University of Arizona                      | AZ                |        121 |   80874783.00
 Purdue University                          | IN                |        151 |   76695016.00
 University of Minnesota-Twin Cities        | MN                |        144 |   76078297.00
(10 rows)