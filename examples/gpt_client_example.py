#!/usr/bin/env python3
"""
Cross-Mind Consensus API Client Example
This script demonstrates how to use the Cross-Mind Consensus API with the GPT configuration.
"""

import requests
import yaml
import json
import time
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_config(config_path):
    """Load the GPT client configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def get_consensus(config, query, options):
    """Get consensus from multiple models on a question with options."""
    base_url = config['api']['baseUrl']
    api_key = config['api']['apiKey']
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}" if api_key else None
    }
    
    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}
    
    payload = {
        'query': query,
        'options': options
    }
    
    try:
        response = requests.post(
            f"{base_url}/consensus", 
            headers=headers,
            json=payload,
            timeout=config['api']['timeouts']['request']
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def print_consensus_result(result):
    """Print the consensus result in a formatted way."""
    if not result:
        return
    
    print("\n" + "="*60)
    print(f"QUERY: {result['query']}")
    print("="*60)
    
    consensus = result['consensus']
    print(f"\nCONSENSUS RESULT:")
    print(f"  Selected option: {consensus['selected_option']['text']} (ID: {consensus['selected_option']['id']})")
    print(f"  Agreement: {consensus['agreement_percentage']:.1f}%")
    print(f"  Vote count: {consensus['vote_count']}")
    
    print("\nMODEL RESPONSES:")
    for idx, response in enumerate(result['model_responses'], 1):
        print(f"\n  Model {idx}: {response['model']}")
        print(f"    Selected: {response['selected_option_id']}")
        print(f"    Confidence: {response['confidence']:.2f}")
        print(f"    Reasoning: {response['reasoning'][:100]}...")
    
    print(f"\nTotal processing time: {result['processing_time']:.3f} seconds")
    print("="*60 + "\n")

def main():
    # Load the configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'config', 'gpt', 'gpt_client.yaml')
    config = load_config(config_path)
    
    # Example questions and options
    examples = [
        {
            'query': "What is the best programming language?",
            'options': [
                {'id': 'python', 'text': 'Python'},
                {'id': 'javascript', 'text': 'JavaScript'},
                {'id': 'go', 'text': 'Go'}
            ]
        },
        {
            'query': "Which cloud provider is best for AI workloads?",
            'options': [
                {'id': 'aws', 'text': 'Amazon Web Services'},
                {'id': 'azure', 'text': 'Microsoft Azure'},
                {'id': 'gcp', 'text': 'Google Cloud Platform'}
            ]
        }
    ]
    
    # Process each example
    for example in examples:
        result = get_consensus(config, example['query'], example['options'])
        print_consensus_result(result)
        time.sleep(1)  # Small delay between requests

if __name__ == "__main__":
    main()