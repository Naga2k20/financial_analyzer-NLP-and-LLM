import PyPDF2
import re
import matplotlib.pyplot as plt
import os

def extract_text_from_file(file_path):
    """Extract text from PDF or TXT file"""
    try:
        if file_path.lower().endswith('.pdf'):
            # PDF file
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text if text.strip() else "No readable text found in PDF"
        
        elif file_path.lower().endswith('.txt'):
            # Text file
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        else:
            return f"Unsupported file type: {file_path}"
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

def extract_financial_metrics(text):
    """Extract financial metrics from text"""
    metrics = {}
    
    financial_terms = {
        'revenue': [r'revenue.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 
                   r'sales.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
        'net_income': [r'net income.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                      r'net profit.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
        'assets': [r'total assets.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
        'profit': [r'profit.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
        'ebitda': [r'ebitda.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)']
    }
    
    for metric, patterns in financial_terms.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', '').replace('$', ''))
                    metrics[metric] = value
                    break
                except:
                    continue
    return metrics

def generate_summary(text):
    """Generate summary from text"""
    if len(text) < 100:
        return "Document too short for meaningful analysis."
    
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
    if sentences:
        summary = '. '.join(sentences[:3]) + '.'
    else:
        summary = "Content extracted but no clear sentence structure found."
    
    return summary

def create_chart(metrics, output_file='financial_chart.png'):
    """Create and save financial chart"""
    if not metrics:
        print("No metrics to visualize.")
        return
    
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        names = [name.replace('_', ' ').title() for name in metrics.keys()]
        values = list(metrics.values())
        
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        bars = ax.bar(names, values, color=colors[:len(names)])
        ax.set_title('Financial Metrics Analysis', fontsize=14, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}', 
                   ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved as: {output_file}")
        return output_file
    except Exception as e:
        print(f"Chart error: {e}")
        return None

def analyze_file(file_path):
    """Main analysis function"""
    print("=" * 60)
    print("🚀 FINANCIAL REPORT ANALYZER")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("💡 Make sure you type the filename correctly without quotes")
        print("💡 Available files in current directory:")
        
        # Show available files
        files = os.listdir('.')
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        txt_files = [f for f in files if f.lower().endswith('.txt')]
        
        if pdf_files:
            print("   PDF files: " + ", ".join(pdf_files))
        if txt_files:
            print("   TXT files: " + ", ".join(txt_files))
        if not pdf_files and not txt_files:
            print("   No PDF or TXT files found")
        
        return
    
    print(f"📁 Analyzing: {file_path}")
    print("-" * 60)
    
    # Extract text
    text = extract_text_from_file(file_path)
    print(f"📄 Text extracted: {len(text)} characters")
    
    # Generate analysis
    summary = generate_summary(text)
    metrics = extract_financial_metrics(text)
    
    # Display results
    print("\n📋 EXECUTIVE SUMMARY:")
    print("-" * 40)
    print(summary)
    
    print("\n💰 FINANCIAL METRICS:")
    print("-" * 40)
    if metrics:
        for metric, value in metrics.items():
            print(f"• {metric.replace('_', ' ').title():<15}: ${value:,.2f}")
    else:
        print("No financial metrics detected.")
        print("Try using a standard financial report with clear numbers.")
    
    # Create chart
    if metrics:
        chart_file = create_chart(metrics)
        if chart_file:
            print(f"\n📈 Chart created: {chart_file}")
            print("💡 Open the PNG file to view the visualization")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")

def main():
    print("🚀 Financial Report Analyzer (Command Line Version)")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Analyze a PDF or TXT file")
        print("2. Create a test file first")
        print("3. Show available files")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            file_path = input("Enter the path to your file (PDF or TXT): ").strip()
            # Remove quotes if user entered them
            file_path = file_path.strip('"\'')
            if file_path:
                analyze_file(file_path)
            else:
                print("❌ Please enter a valid file path.")
        
        elif choice == '2':
            create_test_file()
        
        elif choice == '3':
            print("\n📁 Available files in current directory:")
            files = os.listdir('.')
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            txt_files = [f for f in files if f.lower().endswith('.txt')]
            py_files = [f for f in files if f.lower().endswith('.py')]
            
            if pdf_files:
                print("PDF files: " + ", ".join(pdf_files))
            if txt_files:
                print("TXT files: " + ", ".join(txt_files))
            if py_files:
                print("Python files: " + ", ".join(py_files))
            if not pdf_files and not txt_files:
                print("No PDF or TXT files found. Use option 2 to create a test file.")
        
        elif choice == '4':
            print("👋 Thank you for using Financial Report Analyzer!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def create_test_file():
    """Create a test file with sample financial data"""
    test_content = """ANNUAL FINANCIAL REPORT 2024
TechCorp International

FINANCIAL HIGHLIGHTS:
Total Revenue: $15,750,000
Net Income: $2,845,000
Total Assets: $12,500,000
Operating Profit: $3,200,000
EBITDA: $4,100,000

BUSINESS OVERVIEW:
This was a transformative year for TechCorp International. Our revenue grew by 22% compared to the previous year. We successfully expanded into new markets and improved operational efficiency.
"""
    
    # Create text file
    text_file = "test_financial_report.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Sample financial data saved as: {text_file}")
    print("📊 You can now analyze this file using Option 1!")
    print("💡 Just enter: test_financial_report.txt")

if __name__ == "__main__":
    main()