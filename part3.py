import pandas as pd

from main import Experiment
from main import extract_sentence_representation
import pandas as pd
import matplotlib
import seaborn as sns
import numpy as np
from plot import run_pca_and_plot

exp_2 = Experiment('EXP2.pkl', "vectors_384sentences.GV42B300.average.txt", "stimuli_384sentences.txt")
exp_3 = Experiment('EXP3.pkl', "vectors_243sentences.GV42B300.average.txt", "stimuli_243sentences.txt")
K = 2


# create a list of all categories for exp
def exp_categories_names(exp):
    exp_names = [arr[0] for arr in exp_3.keyPassageCategory[0]]
    return exp_names


# create a list that every entry represents the category of the sentence by order

def vector_to_category(vectors):
    vec_to_category = []
    for sent_idx, sent in enumerate(vectors):
        sentence_idx = exp_3.labelsSentences[sent_idx - 1][0]
        passage_idx = exp_3.labelsPassageForEachSentence[sentence_idx - 1][0]
        category_idx = exp_3.labelsPassageCategory[passage_idx - 1][0]
        category_name = exp_3.keyPassageCategory[0][category_idx - 1][0]
        vec_to_category.append(category_name)
    return vec_to_category




# -----------------------------------------------------------------------------------------------------------------

def run_all(vectors, exp_names, K, embedding_name):
    cat_all_vectors, clusters_per_vec, avg_vectors_per_category_list, category_to_cluster = run_kmeans(
        vectors, exp_names, K=K)
    # run_tsne_and_plot(vectors_matrix=vectors, names=cat_all_vectors, labels=clusters_per_vec,
    #                   embedding_name=embedding_name, K=K, plot_names=False)
    # run_tsne_and_plot(vectors_matrix=np.array(avg_vectors_per_category_list), names=exp_names,
    #                   labels=list(category_to_cluster.values()), embedding_name=f'{embedding_name}_avg', K=K)
    # run_umap_and_plot(vectors_matrix=vectors, names=cat_all_vectors, labels=clusters_per_vec,
    #                   embedding_name=embedding_name, K=K, plot_names=False)
    # run_umap_and_plot(vectors_matrix=np.array(avg_vectors_per_category_list), names=exp_names,
    #                   labels=list(category_to_cluster.values()), embedding_name=f'{embedding_name}_avg', K=K)
    run_pca_and_plot(vectors_metrix=vectors, names=cat_all_vectors, labels=clusters_per_vec,
                     embedding_name=embedding_name, K=K, plot_names=False)
    run_pca_and_plot(vectors_metrix=np.array(avg_vectors_per_category_list), names=exp_names,
                     labels=list(category_to_cluster.values()), embedding_name=f'{embedding_name}_avg', K=K)


# running
exp3_names = exp_categories_names(exp_3)  # 24 names of topics
categories_all_vectors = vector_to_category(exp_3.vectors)  # vec of 384 categories
run_all(exp_3.vectors, exp3_names, K, "original_vectors")
run_all(exp_3.bert_representations, exp3_names, K, 'BERT_vectors')
run_all(exp_3.Fmridata, exp3_names, K, "Fmri_vectors")
