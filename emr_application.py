import pandas as pd
import matplotlib.pyplot as plt
import requests

# Function to fetch and clean patient data from API
def fetch_and_clean_data(url):
    """
    Fetch patient data from an API and clean it for analysis.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data)
        df["name"] = df["name"].astype(str).str.strip().str.title()
        df["email"] = df["email"].astype(str).str.lower()

        # Simulated ages
        df["age"] = [20, 24, 30, 33, 35, 40, 44, 50, 53, 60]
        df["age"] = pd.to_numeric(df["age"], errors="coerce")

        return df

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to the API.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return pd.DataFrame()


# Function to filter patients by age range
def filter_by_age(patient_data, min_age, max_age):
    """
    Filter patients by a specified age range.
    """
    try:
        return patient_data[(patient_data["age"] >= min_age) & (patient_data["age"] <= max_age)]
    except KeyError:
        print("Error: 'age' column not found.")
        return pd.DataFrame()


# Function to analyze data
def analyze_data(df):
    """
    Analyze patient data to calculate key metrics.
    """
    if df.empty:
        return {"total_patients": 0, "unique_domains": 0, "condition_counts": {}, "mean_age": 0}

    try:
        total_patients = len(df)
        unique_domains = df["email"].str.split("@", expand=True)[1].nunique()

        # Simulated condition counts
        condition_counts = {
            "Flu": 3,
            "Hypertension": 2,
            "Diabetes": 1,
            "Asthma": 2,
            "Allergies": 2
        }

        mean_age = df["age"].mean()

        return {
            "total_patients": total_patients,
            "unique_domains": unique_domains,
            "condition_counts": condition_counts,
            "mean_age": mean_age
        }

    except KeyError as err:
        print(f"Error: Missing key {err} in data.")
        return {"total_patients": 0, "unique_domains": 0, "condition_counts": {}, "mean_age": 0}


# Function to visualize data
def visualize_data(analysis, df, filtered=False):
    """
    Create visualizations of the analysis results.
    """
    if not analysis["condition_counts"]:
        print("No data to visualize.")
        return

    condition_counts = analysis["condition_counts"]

    # Bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(condition_counts.keys(), condition_counts.values(), color="skyblue")
    plt.xlabel("Conditions")
    plt.ylabel("Number of Patients")
    plt.title("Prevalence of Conditions in EMR Data")
    plt.tight_layout()
    plt.savefig("conditions_plot.png")
    plt.close()

    # Pie chart
    plt.figure(figsize=(8, 6))
    colors = ["lightblue", "lightgreen", "lightcoral", "lightsalmon", "plum"]
    plt.pie(
        condition_counts.values(),
        labels=condition_counts.keys(),
        autopct="%1.1f%%",
        colors=colors[:len(condition_counts)]
    )
    plt.title("Distribution of Conditions in EMR Data")
    plt.tight_layout()
    plt.savefig("conditions_pie.png")
    plt.close()

    # Age histogram
    if "age" in df.columns and not df["age"].empty:
        plt.figure(figsize=(8, 6))
        plt.hist(
            df["age"],
            bins=[20, 30, 40, 50, 60, 70],
            color="lightcoral",
            edgecolor="black",
            linewidth=2
        )
        plt.xticks([20,30,40,50,60,70])
        plt.xlabel("Age")
        plt.ylabel("Number of Patients")
        plt.title("Age Distribution of Patients" + (" (Filtered)" if filtered else ""))
        plt.tight_layout()
        plt.savefig("filtered_age_distribution.png" if filtered else "age_distribution.png")
        plt.close()


# Function to save analysis
def save_analysis(analysis, filename="analysis_summary.txt"):
    """
    Save analysis results to a file.
    """
    try:
        with open(filename, "w") as file:
            file.write("Analysis Summary\n")
            file.write("----------------\n")
            file.write(f"Total Patients: {analysis['total_patients']}\n")
            file.write(f"Unique Email Domains: {analysis['unique_domains']}\n")
            file.write(f"Mean Age: {analysis['mean_age']}\n")
            file.write("Condition Frequencies:\n")
            for condition, count in analysis["condition_counts"].items():
                file.write(f"- {condition}: {count}\n")
    except IOError as err:
        print(f"Error saving analysis: {err}")


# Main program
def main():
    url = "https://jsonplaceholder.typicode.com/users"
    patient_data = pd.DataFrame()
    filtered_data = pd.DataFrame()

    print("\nWelcome to the Sunrise Hospital EMR System")

    while True:
        print("\nOptions:")
        print("1. Fetch new patient data")
        print("2. Filter patients by age range")
        print("3. View analysis and visualizations")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            patient_data = fetch_and_clean_data(url)
            filtered_data = pd.DataFrame()
            if not patient_data.empty:
                print("Patient data fetched and cleaned successfully.")
            else:
                print("Failed to fetch patient data.")

        elif choice == "2":
            if patient_data.empty:
                print("No data available. Please fetch data first.")
                continue

            try:
                min_age = int(input("Enter minimum age: ").strip())
                max_age = int(input("Enter maximum age: ").strip())
            except ValueError:
                print("Please enter valid numeric ages.")
                continue

            filtered_data = filter_by_age(patient_data, min_age, max_age)

            if not filtered_data.empty:
                print(f"\nFiltered Patients (Ages {min_age}-{max_age}):")
                print(filtered_data[["name", "email", "age"]])
            else:
                print("No patients found in this age range.")

        elif choice == "3":
            if patient_data.empty:
                print("No data available. Please fetch data first.")
                continue

            analysis_df = filtered_data if not filtered_data.empty else patient_data
            analysis = analyze_data(analysis_df)

            visualize_data(analysis, analysis_df, filtered=not filtered_data.empty)
            save_analysis(
                analysis,
                "filtered_analysis_summary.txt" if not filtered_data.empty else "analysis_summary.txt"
            )

            print("\nSunrise Hospital EMR System")
            print("Analysis Results:")
            print(f"Total Patients: {analysis['total_patients']}")
            print(f"Unique Email Domains: {analysis['unique_domains']}")
            print(f"Mean Age: {analysis['mean_age']}")
            print("Condition Frequencies:")
            for condition, count in analysis["condition_counts"].items():
                print(f"- {condition}: {count}")

            max_condition = max(analysis["condition_counts"].items(), key=lambda x: x[1])
            if max_condition[1] > 3:
                print(f"Recommendation: Focus on {max_condition[0]} as it affects {max_condition[1]} patients.")

            print("Visualizations Generated:")
            print("- conditions_plot.png: Bar chart of condition prevalence")
            print("- conditions_pie.png: Pie chart of condition distribution")
            print("- " + ("filtered_age_distribution.png" if not filtered_data.empty else "age_distribution.png")
                  + ": Histogram of age distribution")

        elif choice == "4":
            print("Exiting the EMR System. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()




               
                                   

                                               
    