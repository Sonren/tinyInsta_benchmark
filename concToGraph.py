import pandas as pd
import matplotlib.pyplot as plt
import sys
import os


def create_barplot_with_variance(csv_file, output_file, title, xlabel):

    if not os.path.exists(csv_file):
        print(f"❌ Fichier {csv_file} introuvable!")
        return
    
    df = pd.read_csv(csv_file)
    
    df["AVG_TIME"] = pd.to_numeric(df["AVG_TIME"], errors="coerce")
    df["AVG_TIME"] = df["AVG_TIME"] / 1000 #convert to seconds
    
    stats = df.groupby("PARAM")["AVG_TIME"].agg(['mean', 'std', 'count']) #make all the calculations in this line 
    
    x_labels = stats.index.astype(str)
    means = stats['mean'].values
    stds = stats['std'].values
    
    plt.figure(figsize=(10, 6))
    
    bars = plt.bar(
        x_labels, 
        means, 
        yerr=stds,             
        capsize=10,              
        color='steelblue', 
        edgecolor='black',
        linewidth=1.2,
        alpha=0.8,
        error_kw={'linewidth': 2, 'ecolor': 'black'}  
    )
    
    for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2., 
            height + std + (max(means) * 0.02),
            f'{mean:.2f}s\n±{std:.3f}',
            ha='center', 
            va='bottom', 
            fontsize=9,
            fontweight='bold'
        )
    
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel("Temps moyen par requête (s)", fontsize=12, fontweight='bold')
    plt.xticks(rotation=0, fontsize=11)
    plt.yticks(fontsize=11)
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.close()


def main():
    csv_dir = "outAsync"
    
    benchmarks = [
        {
            'csv': f'{csv_dir}/conc.csv',
            'png': f'{csv_dir}/graphs/conc.png',
            'title': 'Temps moyen par requête selon la concurrence\n(1000 users, 50 posts/user, 20 follows)',
            'xlabel': "Nombre d'utilisateurs concurrents"
        },
        {
            'csv': f'{csv_dir}/post.csv',
            'png': f'{csv_dir}/graphs/post.png',
            'title': 'Temps moyen par requête selon le nombre de posts\n(1000 users, 20 follows, 50 concurrent)',
            'xlabel': 'Nombre de posts par utilisateur'
        },
        {
            'csv': f'{csv_dir}/fanout.csv',
            'png': f'{csv_dir}/graphs/fanout.png',
            'title': 'Temps moyen par requête selon le fanout\n(1000 users, 100 posts/user, 50 concurrent)',
            'xlabel': 'Nombre de followees par utilisateur'
        }
    ]
    
    for benchmark in benchmarks: #check if the csv file exists and create the barplot
        if os.path.exists(benchmark['csv']):
            create_barplot_with_variance(
                benchmark['csv'],
                benchmark['png'],
                benchmark['title'],
                benchmark['xlabel']
            )
        else:
            print(f"⚠️  {benchmark['csv']} introuvable, ignoré")
    
    for benchmark in benchmarks:
        if os.path.exists(benchmark['png']):
            print(f"  ✓ {benchmark['png']}")


if __name__ == '__main__':
    main()