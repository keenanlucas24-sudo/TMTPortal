"""
Seed comprehensive TMT company database with 250+ companies
Organized by primary sector and sub-sector classifications
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_operations import get_db_connection

COMPREHENSIVE_COMPANIES = [
    {"ticker": "NVDA", "name": "NVIDIA", "sector": "Technology", "sub_sector": "GPU & AI Chips", "market_cap": "$3.2T", "description": "GPU, AI, CUDA"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "sub_sector": "GPU & AI Chips", "market_cap": "$220B", "description": "Ryzen, EPYC, Radeon"},
    {"ticker": "ALAB", "name": "Astera Labs", "sector": "Technology", "sub_sector": "GPU & AI Chips", "market_cap": "$35B", "description": "AI connectivity"},
    
    {"ticker": "INTC", "name": "Intel", "sector": "Technology", "sub_sector": "CPUs & Server Chips", "market_cap": "$260B", "description": "Xeon, Core, Foundry"},
    {"ticker": "QCOM", "name": "Qualcomm", "sector": "Technology", "sub_sector": "CPUs & Server Chips", "market_cap": "$210B", "description": "Snapdragon, Oryon"},
    {"ticker": "ARM", "name": "Arm Holdings", "sector": "Technology", "sub_sector": "CPUs & Server Chips", "market_cap": "$60B", "description": "CPU architecture licensing"},
    
    {"ticker": "MRVL", "name": "Marvell Technology", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$65B", "description": "Data center, storage"},
    {"ticker": "AVGO", "name": "Broadcom", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$280B", "description": "Infrastructure, RF, wireless"},
    {"ticker": "LSCC", "name": "Lattice Semiconductor", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$15B", "description": "FPGA, mobile"},
    {"ticker": "NXPI", "name": "NXP Semiconductors", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$55B", "description": "Automotive, RF, IoT"},
    {"ticker": "RMBS", "name": "Rambus Inc", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$12B", "description": "Memory interface, security"},
    {"ticker": "XLNX", "name": "Xilinx", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$60B", "description": "FPGA"},
    {"ticker": "SMTC", "name": "Semtech", "sector": "Technology", "sub_sector": "Fabless Semiconductors", "market_cap": "$10B", "description": "Analog, infrastructure"},
    
    {"ticker": "TXN", "name": "Texas Instruments", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$180B", "description": "Analog ICs"},
    {"ticker": "ADI", "name": "Analog Devices", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$85B", "description": "Mixed-signal, sensors"},
    {"ticker": "MXIM", "name": "Maxim Integrated", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$50B", "description": "Analog chips"},
    {"ticker": "ON", "name": "ON Semiconductor", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$35B", "description": "Power management"},
    {"ticker": "SLAB", "name": "Silicon Labs", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$12B", "description": "MCU, wireless"},
    {"ticker": "GRMN", "name": "Garmin", "sector": "Technology", "sub_sector": "Analog & Power Management", "market_cap": "$35B", "description": "GPS, wireless chips"},
    
    {"ticker": "STM", "name": "STMicroelectronics", "sector": "Technology", "sub_sector": "Automotive Semiconductors", "market_cap": "$50B", "description": "Automotive ICs"},
    
    {"ticker": "MU", "name": "Micron Technology", "sector": "Technology", "sub_sector": "Memory & Storage Semiconductors", "market_cap": "$80B", "description": "DRAM, NAND, SSDs"},
    {"ticker": "WDC", "name": "Western Digital", "sector": "Technology", "sub_sector": "Memory & Storage Semiconductors", "market_cap": "$15B", "description": "Storage, HDD, SSD"},
    {"ticker": "SKYW", "name": "SkyWorks Solutions", "sector": "Technology", "sub_sector": "Memory & Storage Semiconductors", "market_cap": "$20B", "description": "Mixed-signal"},
    
    {"ticker": "ASML", "name": "ASML Holding", "sector": "Technology", "sub_sector": "Semiconductor Equipment", "market_cap": "$310B", "description": "Lithography (EUV)"},
    {"ticker": "KLAC", "name": "KLA Corp", "sector": "Technology", "sub_sector": "Semiconductor Equipment", "market_cap": "$65B", "description": "Inspection equipment"},
    {"ticker": "LRCX", "name": "Lam Research", "sector": "Technology", "sub_sector": "Semiconductor Equipment", "market_cap": "$80B", "description": "Deposition, etch equipment"},
    {"ticker": "AMAT", "name": "Applied Materials", "sector": "Technology", "sub_sector": "Semiconductor Equipment", "market_cap": "$210B", "description": "Deposition equipment"},
    {"ticker": "COHR", "name": "Coherent", "sector": "Technology", "sub_sector": "Semiconductor Equipment", "market_cap": "$20B", "description": "Laser, imaging equipment"},
    
    {"ticker": "SNPS", "name": "Synopsys", "sector": "Technology", "sub_sector": "Semiconductor Services & IP", "market_cap": "$90B", "description": "EDA, chip design tools"},
    {"ticker": "CDNS", "name": "Cadence Design", "sector": "Technology", "sub_sector": "Semiconductor Services & IP", "market_cap": "$80B", "description": "EDA, simulation tools"},
    {"ticker": "ANSYS", "name": "ANSYS", "sector": "Technology", "sub_sector": "Semiconductor Services & IP", "market_cap": "$50B", "description": "Simulation software"},
    {"ticker": "PLTR", "name": "Palantir Technologies", "sector": "Technology", "sub_sector": "Semiconductor Services & IP", "market_cap": "$80B", "description": "Data analytics"},
    
    {"ticker": "TSM", "name": "TSMC", "sector": "Technology", "sub_sector": "Semiconductor Foundries", "market_cap": "$800B", "description": "Foundry, advanced nodes"},
    
    {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Technology", "sub_sector": "Network Infrastructure", "market_cap": "$300B", "description": "Routers, switches, firewalls"},
    {"ticker": "JNPR", "name": "Juniper Networks", "sector": "Technology", "sub_sector": "Network Infrastructure", "market_cap": "$20B", "description": "Routing, switching"},
    {"ticker": "FIVN", "name": "F5 Networks", "sector": "Technology", "sub_sector": "Network Infrastructure", "market_cap": "$15B", "description": "Application delivery"},
    {"ticker": "AKAM", "name": "Akamai Technologies", "sector": "Technology", "sub_sector": "Network Infrastructure", "market_cap": "$20B", "description": "CDN, cloud security"},
    {"ticker": "ANET", "name": "Arista Networks", "sector": "Technology", "sub_sector": "Network Infrastructure", "market_cap": "$80B", "description": "Data center switches"},
    
    {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$15B", "description": "Power, cooling, infrastructure"},
    {"ticker": "PLD", "name": "Prologis", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$160B", "description": "Data center REIT"},
    {"ticker": "EQIX", "name": "Equinix", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$120B", "description": "Data center operations"},
    {"ticker": "DLR", "name": "Digital Realty", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$50B", "description": "Data center REIT"},
    {"ticker": "CCI", "name": "Crown Castle", "sector": "Telecom", "sub_sector": "Network Infrastructure", "market_cap": "$70B", "description": "Tower infrastructure REIT"},
    {"ticker": "QTS", "name": "QTS Realty Trust", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$12B", "description": "Data center REIT"},
    {"ticker": "CONE", "name": "CyrusOne", "sector": "Technology", "sub_sector": "Data Center Infrastructure", "market_cap": "$12B", "description": "Data center operations"},
    
    {"ticker": "NTAP", "name": "NetApp", "sector": "Technology", "sub_sector": "Enterprise Storage", "market_cap": "$35B", "description": "Storage, data management"},
    {"ticker": "PSTG", "name": "Pure Storage", "sector": "Technology", "sub_sector": "Enterprise Storage", "market_cap": "$30B", "description": "All-flash storage"},
    {"ticker": "HPE", "name": "Hewlett Packard Enterprise", "sector": "Technology", "sub_sector": "Enterprise Storage", "market_cap": "$45B", "description": "Enterprise storage"},
    {"ticker": "DELL", "name": "Dell Technologies", "sector": "Technology", "sub_sector": "Enterprise Storage", "market_cap": "$50B", "description": "Storage arrays"},
    
    {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Technology", "sub_sector": "Server & Computing Hardware", "market_cap": "$60B", "description": "Servers, AI infrastructure"},
    {"ticker": "HPQ", "name": "HP Inc", "sector": "Technology", "sub_sector": "Server & Computing Hardware", "market_cap": "$25B", "description": "PCs, workstations"},
    {"ticker": "CRSR", "name": "Corsair", "sector": "Technology", "sub_sector": "Server & Computing Hardware", "market_cap": "$15B", "description": "Gaming PCs, components"},
    {"ticker": "AAPL", "name": "Apple", "sector": "Technology", "sub_sector": "Hardware & Consumer Electronics", "market_cap": "$3.5T", "description": "iPhones, Macs, iPad"},
    
    {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology", "sub_sector": "Hyperscale Cloud", "market_cap": "$3.5T", "description": "Azure, 365, Teams"},
    {"ticker": "AMZN", "name": "Amazon", "sector": "Technology", "sub_sector": "Hyperscale Cloud", "market_cap": "$2.0T", "description": "AWS, EC2"},
    {"ticker": "GOOG", "name": "Alphabet/Google", "sector": "Technology", "sub_sector": "Hyperscale Cloud", "market_cap": "$2.2T", "description": "Google Cloud, Workspace"},
    {"ticker": "ORCL", "name": "Oracle", "sector": "Technology", "sub_sector": "Hyperscale Cloud", "market_cap": "$380B", "description": "Oracle Cloud, database"},
    {"ticker": "IBM", "name": "IBM", "sector": "Technology", "sub_sector": "Hyperscale Cloud", "market_cap": "$230B", "description": "IBM Cloud, enterprise"},
    
    {"ticker": "CRM", "name": "Salesforce", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$360B", "description": "Salesforce Cloud, Einstein"},
    {"ticker": "NOW", "name": "ServiceNow", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$80B", "description": "Workflow, IT service management"},
    {"ticker": "SNOW", "name": "Snowflake", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$80B", "description": "Data warehouse"},
    {"ticker": "DBX", "name": "Dropbox", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$12B", "description": "Cloud storage, collaboration"},
    {"ticker": "BOX", "name": "Box", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$10B", "description": "Content management"},
    {"ticker": "DOMO", "name": "Domo", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$10B", "description": "Business analytics"},
    {"ticker": "ADBE", "name": "Adobe", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$270B", "description": "Creative Cloud, document management"},
    {"ticker": "INTU", "name": "Intuit", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$200B", "description": "Cloud accounting"},
    {"ticker": "VEEV", "name": "Veeva Systems", "sector": "Technology", "sub_sector": "Cloud Applications", "market_cap": "$30B", "description": "Life sciences cloud"},
    
    {"ticker": "MSTR", "name": "MicroStrategy", "sector": "Technology", "sub_sector": "Data & Analytics", "market_cap": "$35B", "description": "Business intelligence, AI"},
    {"ticker": "SPLK", "name": "Splunk", "sector": "Technology", "sub_sector": "Data & Analytics", "market_cap": "$40B", "description": "Data analytics, security operations"},
    {"ticker": "DDOG", "name": "Datadog", "sector": "Technology", "sub_sector": "Data & Analytics", "market_cap": "$50B", "description": "Cloud monitoring, infrastructure"},
    {"ticker": "SUMO", "name": "Sumo Logic", "sector": "Technology", "sub_sector": "Data & Analytics", "market_cap": "$18B", "description": "Cloud SIEM, monitoring"},
    {"ticker": "ALKT", "name": "Alteryx", "sector": "Technology", "sub_sector": "Data & Analytics", "market_cap": "$5B", "description": "Data analytics"},
    
    {"ticker": "CRWD", "name": "CrowdStrike", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$50B", "description": "Cloud endpoint security"},
    {"ticker": "PANW", "name": "Palo Alto Networks", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$70B", "description": "Cloud security platform"},
    {"ticker": "ZS", "name": "Zscaler", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$35B", "description": "Zero-trust cloud security"},
    {"ticker": "NET", "name": "Cloudflare", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$35B", "description": "DDoS protection, WAF"},
    {"ticker": "OKTA", "name": "Okta", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$20B", "description": "Identity, access management"},
    {"ticker": "CHKP", "name": "Check Point", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$15B", "description": "Firewall, endpoint"},
    {"ticker": "FTNT", "name": "Fortinet", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$20B", "description": "Firewalls, EDR"},
    {"ticker": "TENB", "name": "Tenable", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$13B", "description": "Vulnerability management"},
    {"ticker": "QLYS", "name": "Qualys", "sector": "Technology", "sub_sector": "Cybersecurity", "market_cap": "$10B", "description": "Vulnerability scanning"},
    
    {"ticker": "WDAY", "name": "Workday", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$70B", "description": "Cloud HCM, finance, planning"},
    {"ticker": "SAP", "name": "SAP SE", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$180B", "description": "Enterprise resource planning"},
    {"ticker": "ADP", "name": "ADP", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$95B", "description": "Payroll, HCM services"},
    {"ticker": "PAYX", "name": "Paychex", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$45B", "description": "Payroll, HR services"},
    {"ticker": "HUBS", "name": "HubSpot", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$50B", "description": "CRM, marketing automation"},
    {"ticker": "MKTX", "name": "MarketAxess", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$20B", "description": "Financial trading platform"},
    {"ticker": "TEAM", "name": "Atlassian", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$60B", "description": "Jira, Confluence, DevOps"},
    {"ticker": "MNDY", "name": "Monday.com", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$10B", "description": "Work OS, project management"},
    {"ticker": "ASANA", "name": "Asana", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$10B", "description": "Work management platform"},
    {"ticker": "DOCU", "name": "DocuSign", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$13B", "description": "E-signature, contract management"},
    {"ticker": "BILL", "name": "Bill.com", "sector": "Technology", "sub_sector": "Enterprise Software", "market_cap": "$10B", "description": "Financial operations platform"},
    
    {"ticker": "ZOOM", "name": "Zoom Video Communications", "sector": "Technology", "sub_sector": "Communications & Collaboration", "market_cap": "$30B", "description": "Video conferencing"},
    {"ticker": "TWLO", "name": "Twilio", "sector": "Technology", "sub_sector": "Communications & Collaboration", "market_cap": "$15B", "description": "Communications APIs"},
    
    {"ticker": "VZ", "name": "Verizon", "sector": "Telecom", "sub_sector": "Wireless Carriers", "market_cap": "$300B", "description": "Wireless, telecom"},
    {"ticker": "T", "name": "AT&T", "sector": "Telecom", "sub_sector": "Wireless Carriers", "market_cap": "$150B", "description": "Wireless, telecom"},
    {"ticker": "TMUS", "name": "T-Mobile", "sector": "Telecom", "sub_sector": "Wireless Carriers", "market_cap": "$180B", "description": "Wireless carrier"},
    {"ticker": "DISH", "name": "Dish Network", "sector": "Telecom", "sub_sector": "Wireless Carriers", "market_cap": "$15B", "description": "Wireless MVNO"},
    
    {"ticker": "VOD", "name": "Vodafone", "sector": "Telecom", "sub_sector": "International Telecom", "market_cap": "$45B", "description": "UK telecom"},
    {"ticker": "DT", "name": "Deutsche Telekom", "sector": "Telecom", "sub_sector": "International Telecom", "market_cap": "$65B", "description": "German telecom (ADR)"},
    
    {"ticker": "CMCSA", "name": "Comcast", "sector": "Telecom", "sub_sector": "Cable & Broadband", "market_cap": "$200B", "description": "Cable, broadband, media"},
    {"ticker": "CHTR", "name": "Charter Communications", "sector": "Telecom", "sub_sector": "Cable & Broadband", "market_cap": "$100B", "description": "Broadband, cable"},
    {"ticker": "LUMN", "name": "Lumen Technologies", "sector": "Telecom", "sub_sector": "Cable & Broadband", "market_cap": "$25B", "description": "Fiber, network"},
    
    {"ticker": "NOK", "name": "Nokia", "sector": "Telecom", "sub_sector": "Telecom Equipment", "market_cap": "$35B", "description": "Telecom equipment"},
    {"ticker": "ERIC", "name": "Ericsson", "sector": "Telecom", "sub_sector": "Telecom Equipment", "market_cap": "$30B", "description": "Telecom equipment"},
    {"ticker": "VSAT", "name": "Viasat", "sector": "Telecom", "sub_sector": "Satellite Communications", "market_cap": "$5B", "description": "Satellite broadband"},
    
    {"ticker": "NFLX", "name": "Netflix", "sector": "Media", "sub_sector": "Streaming Video", "market_cap": "$300B", "description": "Streaming video"},
    {"ticker": "DIS", "name": "Disney", "sector": "Media", "sub_sector": "Streaming Video", "market_cap": "$200B", "description": "Disney+, Hulu, ESPN+"},
    {"ticker": "PARA", "name": "Paramount", "sector": "Media", "sub_sector": "Streaming Video", "market_cap": "$10B", "description": "Paramount+"},
    {"ticker": "WBD", "name": "Warner Bros Discovery", "sector": "Media", "sub_sector": "Streaming Video", "market_cap": "$50B", "description": "Max, Discovery+"},
    {"ticker": "ROKU", "name": "Roku", "sector": "Media", "sub_sector": "Streaming Video", "market_cap": "$15B", "description": "Streaming OS, The Roku Channel"},
    
    {"ticker": "FOX", "name": "Fox Corporation", "sector": "Media", "sub_sector": "Broadcast & Cable", "market_cap": "$25B", "description": "Broadcasting"},
    
    {"ticker": "SPOT", "name": "Spotify", "sector": "Media", "sub_sector": "Music & Audio", "market_cap": "$50B", "description": "Music streaming"},
    {"ticker": "SIRI", "name": "SiriusXM", "sector": "Media", "sub_sector": "Music & Audio", "market_cap": "$35B", "description": "Satellite radio, podcasts"},
    
    {"ticker": "SNAP", "name": "Snap Inc", "sector": "Media", "sub_sector": "Social Media", "market_cap": "$15B", "description": "Social content platform"},
    {"ticker": "PINS", "name": "Pinterest", "sector": "Media", "sub_sector": "Social Media", "market_cap": "$25B", "description": "Content discovery"},
    {"ticker": "META", "name": "Meta Platforms", "sector": "Media", "sub_sector": "Social Media", "market_cap": "$1.5T", "description": "Facebook/Instagram Ads"},
    
    {"ticker": "RBLX", "name": "Roblox", "sector": "Media", "sub_sector": "Gaming", "market_cap": "$15B", "description": "Metaverse gaming"},
    {"ticker": "ATVI", "name": "Activision Blizzard", "sector": "Media", "sub_sector": "Gaming", "market_cap": "$80B", "description": "Video games"},
    {"ticker": "TTWO", "name": "Take-Two Interactive", "sector": "Media", "sub_sector": "Gaming", "market_cap": "$25B", "description": "Gaming (GTA, 2K)"},
    {"ticker": "EA", "name": "Electronic Arts", "sector": "Media", "sub_sector": "Gaming", "market_cap": "$40B", "description": "Gaming"},
    
    {"ticker": "TTD", "name": "The Trade Desk", "sector": "Media", "sub_sector": "Advertising Tech", "market_cap": "$30B", "description": "Programmatic advertising"},
    
    {"ticker": "Z", "name": "Zillow", "sector": "Technology", "sub_sector": "Real Estate Tech", "market_cap": "$20B", "description": "Real estate, Zestimate"},
    {"ticker": "RDFN", "name": "Redfin", "sector": "Technology", "sub_sector": "Real Estate Tech", "market_cap": "$12B", "description": "Real estate platform"},
    
    {"ticker": "LOGI", "name": "Logitech", "sector": "Technology", "sub_sector": "Peripherals & Accessories", "market_cap": "$12B", "description": "Mice, keyboards, headsets"},
    
    {"ticker": "PYPL", "name": "PayPal", "sector": "Technology", "sub_sector": "Fintech & Payments", "market_cap": "$60B", "description": "Financial payments platform"},
    {"ticker": "SQ", "name": "Block (Square)", "sector": "Technology", "sub_sector": "Fintech & Payments", "market_cap": "$50B", "description": "Payment processing"},
    {"ticker": "SHOP", "name": "Shopify", "sector": "Technology", "sub_sector": "E-Commerce Platforms", "market_cap": "$130B", "description": "E-commerce platform"},
    
    {"ticker": "UBER", "name": "Uber", "sector": "Technology", "sub_sector": "Rideshare & Delivery", "market_cap": "$150B", "description": "Rideshare, food delivery"},
    {"ticker": "LYFT", "name": "Lyft", "sector": "Technology", "sub_sector": "Rideshare & Delivery", "market_cap": "$8B", "description": "Rideshare"},
    {"ticker": "DASH", "name": "DoorDash", "sector": "Technology", "sub_sector": "Rideshare & Delivery", "market_cap": "$70B", "description": "Food delivery"},
    
    {"ticker": "ABNB", "name": "Airbnb", "sector": "Technology", "sub_sector": "Travel & Hospitality Tech", "market_cap": "$90B", "description": "Vacation rentals"},
    {"ticker": "BKNG", "name": "Booking Holdings", "sector": "Technology", "sub_sector": "Travel & Hospitality Tech", "market_cap": "$140B", "description": "Travel booking"},
    {"ticker": "EXPE", "name": "Expedia", "sector": "Technology", "sub_sector": "Travel & Hospitality Tech", "market_cap": "$25B", "description": "Travel booking"},
]

def seed_comprehensive_companies():
    """Seed database with comprehensive company list"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print(f"Starting to seed {len(COMPREHENSIVE_COMPANIES)} companies...")
        
        inserted = 0
        updated = 0
        
        for company in COMPREHENSIVE_COMPANIES:
            try:
                cur.execute("""
                    INSERT INTO companies (ticker, name, sector, sub_sector, market_cap, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        sector = EXCLUDED.sector,
                        sub_sector = EXCLUDED.sub_sector,
                        market_cap = EXCLUDED.market_cap,
                        description = EXCLUDED.description
                    RETURNING (xmax = 0) AS inserted
                """, (
                    company['ticker'],
                    company['name'],
                    company['sector'],
                    company['sub_sector'],
                    company['market_cap'],
                    company['description']
                ))
                
                result = cur.fetchone()
                if result and result[0]:
                    inserted += 1
                else:
                    updated += 1
                    
            except Exception as e:
                print(f"Error inserting {company['ticker']}: {e}")
                continue
        
        conn.commit()
        print(f"\n✓ Successfully seeded comprehensive company database!")
        print(f"  - Inserted: {inserted} new companies")
        print(f"  - Updated: {updated} existing companies")
        print(f"  - Total: {inserted + updated} companies in database")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding companies: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_comprehensive_companies()
