import json
import random
import os

# Define templates for generating diverse insurance Q&A pairs
premium_templates = [
    {
        "instruction_template": "Calculate my premium for {age} year old with ${car_value} car",
        "response_template": "Your monthly premium is ${monthly}. Breakdown: Base $500 × Age factor {age_factor} × Vehicle factor {vehicle_factor} × Coverage factor 1.5 = ${monthly}. At {age}, you're in the {risk_category} risk category. Your vehicle value of ${car_value} results in a premium of ${monthly:.2f}/month."
    },
    {
        "instruction_template": "What's my monthly premium for a {age}-year-old with a ${car_value} car?",
        "response_template": "Your monthly premium is ${monthly:.2f}. Breakdown: Base $500 × Age factor {age_factor:.1f} × Vehicle factor {vehicle_factor:.2f} × Coverage factor 1.5 = ${monthly:.2f}. At {age}, you're in the {risk_category} risk category."
    },
    {
        "instruction_template": "How much for a {age}-year-old with ${car_value} car?",
        "response_template": "Your premium is ${monthly:.2f}/month or ${yearly:.2f}/year. At {age} years old with a ${car_value} vehicle, the age factor is {age_factor:.1f} and vehicle factor is {vehicle_factor:.2f}."
    }
]

claim_templates = [
    {"instruction": "Check claim status for CL-{claim_id}", "response": "Claim CL-{claim_id} is {status}. {next_steps}"},
    {"instruction": "What's the status of claim CL-{claim_id}?", "response": "Claim CL-{claim_id} is {status}. {next_steps}"},
    {"instruction": "Is claim CL-{claim_id} approved?", "response": "Claim CL-{claim_id} is {status}. {next_steps}"},
    {"instruction": "How do I file a claim for {incident}?", "response": "To file a claim for {incident}, contact your insurer immediately. Provide your policy number and incident details. File a police report if required."},
    {"instruction": "Can I claim for {incident}?", "response": "Yes, {incident} is typically covered under your {policy_type} policy. File a claim within 24 hours and provide documentation."}
]

def calculate_premium(age, car_value):
    """Calculate premium breakdown"""
    if age < 25:
        age_factor = 1.2
        risk_category = "high"
    elif age < 60:
        age_factor = 0.8
        risk_category = "low"
    else:
        age_factor = 1.3
        risk_category = "standard"
    
    vehicle_factor = car_value / 20000
    coverage_factor = 1.5
    monthly = 500 * age_factor * vehicle_factor * coverage_factor
    yearly = monthly * 12
    
    return {
        "monthly": round(monthly, 2),
        "yearly": round(yearly, 2),
        "age_factor": age_factor,
        "vehicle_factor": vehicle_factor,
        "risk_category": risk_category
    }

def generate_premium_queries(num_samples=300):
    """Generate premium calculation queries"""
    queries = []
    ages = list(range(18, 71))
    car_values = [15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 75000, 100000]
    
    for _ in range(num_samples):
        age = random.choice(ages)
        car_value = random.choice(car_values)
        premium_data = calculate_premium(age, car_value)
        
        template = random.choice(premium_templates)
        
        instruction = template["instruction_template"].format(
            age=age,
            car_value=f"{car_value:,}"
        )
        
        response = template["response_template"].format(
            age=age,
            car_value=f"{car_value:,}",
            monthly=premium_data["monthly"],
            yearly=premium_data["yearly"],
            age_factor=premium_data["age_factor"],
            vehicle_factor=premium_data["vehicle_factor"],
            risk_category=premium_data["risk_category"]
        )
        
        queries.append({
            "instruction": instruction,
            "response": response
        })
    
    return queries

def generate_claim_queries(num_samples=200):
    """Generate claim-related queries"""
    queries = []
    claim_statuses = ["Approved", "Pending Review", "Processing", "Paid", "Denied"]
    status_messages = {
        "Approved": "Payment will be processed within 7 days.",
        "Pending Review": "Additional documentation may be required.",
        "Processing": "Claim is being reviewed by adjuster.",
        "Paid": "Payment has been issued.",
        "Denied": "Appeal process available within 30 days."
    }
    incidents = ["car accident", "motorcycle accident", "theft", "fire damage", "windshield damage", "flood damage"]
    policy_types = ["auto", "renters", "health"]
    
    for _ in range(num_samples):
        claim_id = f"CL-{random.randint(1000, 99999)}"
        status = random.choice(claim_statuses)
        incident = random.choice(incidents)
        policy_type = random.choice(policy_types)
        
        template = random.choice(claim_templates)
        
        instruction = template["instruction"].format(
            claim_id=claim_id,
            incident=incident,
            policy_type=policy_type
        )
        
        response = template["response"].format(
            claim_id=claim_id,
            status=status,
            next_steps=status_messages[status],
            incident=incident,
            policy_type=policy_type
        )
        
        queries.append({
            "instruction": instruction,
            "response": response
        })
    
    return queries

def generate_policy_queries(num_samples=300):
    """Generate policy-related queries"""
    queries = []
    items = ["theft", "windshield damage", "flood damage", "fire damage", "liability", 
             "medical bills", "ambulance rides", "vandalism", "hail damage", "falling objects"]
    
    policy_responses = {
        "auto": {
            "theft": "Theft is covered under comprehensive coverage in your auto policy.",
            "windshield damage": "Windshield damage is covered under comprehensive coverage.",
            "flood damage": "Flood damage is not covered under auto insurance.",
            "fire damage": "Fire damage is covered under comprehensive coverage.",
            "liability": "Liability is covered under your auto policy.",
            "medical bills": "Medical bills are covered under PIP or MedPay.",
            "ambulance rides": "Ambulance rides may be covered under PIP.",
            "vandalism": "Vandalism is covered under comprehensive coverage.",
            "hail damage": "Hail damage is covered under comprehensive coverage.",
            "falling objects": "Falling objects are covered under comprehensive coverage."
        },
        "renters": {
            "theft": "Theft is covered under your renters policy.",
            "windshield damage": "Windshield damage is not covered under renters insurance.",
            "flood damage": "Flood damage is not covered under renters insurance.",
            "fire damage": "Fire damage is covered under renters insurance.",
            "liability": "Liability is covered under your renters policy.",
            "medical bills": "Medical bills are not covered under renters insurance.",
            "ambulance rides": "Ambulance rides are not covered under renters insurance.",
            "vandalism": "Vandalism is covered under renters insurance.",
            "hail damage": "Hail damage is not covered under renters insurance.",
            "falling objects": "Falling objects are not covered under renters insurance."
        },
        "health": {
            "theft": "Theft is not covered under health insurance.",
            "windshield damage": "Windshield damage is not covered under health insurance.",
            "flood damage": "Flood damage is not covered under health insurance.",
            "fire damage": "Fire damage is not covered under health insurance.",
            "liability": "Liability is not covered under health insurance.",
            "medical bills": "Medical bills are covered under health insurance.",
            "ambulance rides": "Ambulance rides are covered under health insurance.",
            "vandalism": "Vandalism is not covered under health insurance.",
            "hail damage": "Hail damage is not covered under health insurance.",
            "falling objects": "Falling objects are not covered under health insurance."
        }
    }
    
    for _ in range(num_samples):
        item = random.choice(items)
        policy_type = random.choice(["auto", "renters", "health"])
        
        instruction = f"Does {policy_type} insurance cover {item}?"
        
        response = policy_responses[policy_type].get(item, f"{item.title()} is covered under {policy_type} insurance.")
        
        queries.append({
            "instruction": instruction,
            "response": response
        })
    
    return queries

def generate_comparison_queries(num_samples=100):
    """Generate policy comparison queries"""
    queries = []
    policy_pairs = [
        ["auto", "renters"],
        ["auto", "health"],
        ["renters", "health"],
        ["auto", "renters", "health"]
    ]
    
    policy_descriptions = {
        "auto": "Auto insurance covers vehicle damage and liability while driving.",
        "renters": "Renters insurance covers personal property and liability in your home.",
        "health": "Health insurance covers medical expenses and hospitalization."
    }
    
    for _ in range(num_samples):
        pair = random.choice(policy_pairs)
        instruction = f"Compare {pair[0]} and {pair[1]} insurance" if len(pair) == 2 else "Compare all policies"
        
        response = "Here's a policy comparison:"
        for p in pair:
            response += f"\n- **{p.title()} Insurance**: {policy_descriptions[p]}"
        
        response += "\n\n**Recommendation:** Choose based on your specific needs. Auto for vehicles, Renters for home belongings, Health for medical care."
        
        queries.append({
            "instruction": instruction,
            "response": response
        })
    
    return queries

def generate_general_queries(num_samples=100):
    """Generate general insurance queries"""
    queries = []
    general_questions = [
        "What is comprehensive coverage?",
        "What is liability coverage?",
        "What is the difference between collision and comprehensive?",
        "How does a deductible work?",
        "What is an insurance premium?",
        "What is out-of-pocket maximum?",
        "What is the difference between actual cash value and replacement cost?",
        "Do I need full coverage on my car?",
        "How can I lower my insurance premium?",
        "What factors affect my insurance rate?"
    ]
    
    general_responses = {
        "What is comprehensive coverage?": "Comprehensive coverage pays for damage to your vehicle from non-collision events like theft, vandalism, fire, hail, or hitting an animal.",
        "What is liability coverage?": "Liability coverage protects you if you're at fault in an accident causing injury or property damage to others. It covers legal costs and settlements up to your policy limits.",
        "What is the difference between collision and comprehensive?": "Collision covers damage from hitting another vehicle or object. Comprehensive covers non-collision events: theft, vandalism, fire, hail, flooding, and animal strikes.",
        "How does a deductible work?": "A deductible is the amount you pay out-of-pocket before insurance kicks in. For example, with a $500 deductible and $2,000 damage, you pay $500, insurance pays $1,500.",
        "What is an insurance premium?": "An insurance premium is the amount you pay monthly or yearly for your insurance coverage.",
        "What is out-of-pocket maximum?": "The out-of-pocket maximum is the most you'll pay for covered medical services in a year. After reaching it, your health insurance pays 100% of covered costs.",
        "What is the difference between actual cash value and replacement cost?": "Actual cash value pays the depreciated value of your item. Replacement cost pays the full amount to replace it with a similar new item.",
        "Do I need full coverage on my car?": "Full coverage is recommended if your car is financed or leased. It's also worth considering if your car is newer or has significant value.",
        "How can I lower my insurance premium?": "You can lower your premium by: increasing your deductible, bundling policies, maintaining good credit, and driving safely.",
        "What factors affect my insurance rate?": "Insurance rates are affected by: age, location, driving record, credit score, vehicle type, coverage limits, and annual mileage."
    }
    
    for question in general_questions:
        queries.append({
            "instruction": question,
            "response": general_responses[question]
        })
    
    return queries

def main():
    print("📊 Generating 1,000+ insurance Q&A pairs...")
    
    all_queries = []
    all_queries.extend(generate_premium_queries(300))
    all_queries.extend(generate_claim_queries(200))
    all_queries.extend(generate_policy_queries(300))
    all_queries.extend(generate_comparison_queries(100))
    all_queries.extend(generate_general_queries(100))
    
    # Shuffle for variety
    random.shuffle(all_queries)
    
    # Save to file
    output_file = "training_data/insurance_qa_large.jsonl"
    os.makedirs("training_data", exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for query in all_queries:
            f.write(json.dumps(query) + "\n")
    
    print(f"✅ Generated {len(all_queries)} Q&A pairs")
    print(f"📁 Saved to {output_file}")
    print("\n📊 Sample:")
    sample = random.choice(all_queries)
    print(f"   Q: {sample['instruction']}")
    print(f"   A: {sample['response'][:100]}...")

if __name__ == "__main__":
    main()