from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing  # to normalise existing X
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from get_exp_data import Experiment

RESULTS_PATH = Path("results")


def best_k_kmeans(vectors, vector_type):
    np.random.seed(42)
    k_values = range(2, 15)
    wcss = []
    silhouette_scores = []
    for k in k_values:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(vectors)
        wcss.append(kmeans.inertia_)
        labels = kmeans.labels_
        silhouette_scores.append(silhouette_score(vectors, labels))

    # Plot the WCSS values
    plt.plot(k_values, wcss, marker="o")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("WCSS")
    plt.title("Elbow Method")

    # Find the best value of K
    diff = []
    for i in range(1, len(wcss)):
        diff.append(wcss[i] - wcss[i - 1])

    best_k_wscc = diff.index(max(diff)) + 2

    plt.savefig(RESULTS_PATH / f"{vector_type} Elbow Method best_k={best_k_wscc}.jpg")
    plt.clf()

    # Plot the silhouette scores
    plt.plot(k_values, silhouette_scores, marker="o")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Method")

    best_k_silo = k_values[silhouette_scores.index(max(silhouette_scores))]
    plt.savefig(
        RESULTS_PATH / f"{vector_type} Silhouette Method best_k={best_k_silo}.jpg"
    )
    plt.clf()

    print(f"{best_k_wscc=}")
    return best_k_wscc


def run_kmeans(
    exp: Experiment, avg_categories: bool, vectors, vector_type: str, k: int = None
):
    if avg_categories:
        categories_names = exp.categories_names
    else:
        categories_names = exp.categories_all_vectors

    if not k:
        k = best_k_kmeans(vectors=vectors, vector_type=vector_type)
    kmeans = KMeans(n_clusters=k)
    norm_vectors = preprocessing.normalize(vectors)
    kmeans.fit(norm_vectors)
    clusters_numbers = kmeans.labels_
    # centroids = kmeans.cluster_centers_

    cluster_to_categories = {}
    # for each cluster creates dict of {category: count}
    for idx, cluster_num in enumerate(clusters_numbers):
        category_name = categories_names[idx]
        if cluster_num not in cluster_to_categories.keys():
            cluster_to_categories[cluster_num] = {}  # new count diict
        if category_name not in cluster_to_categories[cluster_num].keys():
            cluster_to_categories[cluster_num][category_name] = 1  # add category
        else:
            cluster_to_categories[cluster_num][category_name] += 1  # increase count

    category_to_cluster = {}
    for category in exp.categories_names:
        chosen_cluster = -1
        max_appearance = 0
        for cluster_num in range(k):
            if category not in cluster_to_categories[cluster_num].keys():
                pass
            else:
                if cluster_to_categories[cluster_num][category] > max_appearance:
                    max_appearance = cluster_to_categories[cluster_num][category]
                    chosen_cluster = cluster_num

        category_to_cluster[category] = chosen_cluster

    cluster_nums_of_all_vectors = [
        category_to_cluster[category] for category in exp.categories_all_vectors
    ]

    return cluster_nums_of_all_vectors, category_to_cluster, k


def calculate_within_distance(cluster_dict):
    within_distances = {}

    # Iterate over each cluster in the dictionary
    for cluster_num, vectors in cluster_dict.items():
        cluster_size = len(vectors)
        if cluster_size <= 1:
            within_distances[cluster_num] = 0.0
            continue

        # Calculate the pairwise distances between vectors in the cluster using cosine similarity
        distances = np.zeros((cluster_size, cluster_size))
        for i in range(cluster_size):
            for j in range(i + 1, cluster_size):
                similarity = cosine_similarity([vectors[i]], [vectors[j]])
                distances[i, j] = 1 - similarity[0, 0]

        # Calculate the sum of pairwise distances
        within_distance = np.sum(distances) / (cluster_size * (cluster_size - 1))

        within_distances[cluster_num] = within_distance

    return within_distances


def calculate_between_distance(cluster_dict):

    # Calculate the centroid for each cluster
    centroids = {}
    for cluster_num, vectors in cluster_dict.items():
        centroid = np.mean(vectors, axis=0)
        centroids[cluster_num] = centroid

    # Compute the pairwise distances between centroids
    cluster_nums = list(cluster_dict.keys())
    num_clusters = len(cluster_nums)
    distances = np.zeros((num_clusters, num_clusters))
    for i in range(num_clusters):
        for j in range(i + 1, num_clusters):
            centroid_i = centroids[cluster_nums[i]]
            centroid_j = centroids[cluster_nums[j]]
            distances[i, j] = np.linalg.norm(centroid_i - centroid_j)

    # Calculate the average pairwise distance between centroids
    between_distance = np.sum(distances) / (num_clusters * (num_clusters - 1))

    return between_distance


def create_fmri_to_cluster(category_to_cluster, exp: Experiment):
    fmri_cluster_num_list = []
    for i, cat in enumerate(exp.categories_all_vectors):
        fmri_cluster_num_list.append(category_to_cluster[cat])
    fmri_dict = {}
    for cluster, vec in zip(fmri_cluster_num_list, exp.fmri_data):
        if cluster not in fmri_dict.keys():
            fmri_dict[cluster] = []
            fmri_dict[cluster].append(vec)
        else:
            fmri_dict[cluster].append(vec)

    return fmri_dict
