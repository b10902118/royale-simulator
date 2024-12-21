import cv2
import numpy as np
import matplotlib.pyplot as plt
from glob import glob


def match_images(query_image_path, dataset_image_paths):
    # Load query image
    query_img = cv2.imread(query_image_path, cv2.IMREAD_GRAYSCALE)
    if query_img is None:
        raise ValueError(f"Query image at {query_image_path} not found.")

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Detect and compute features for query image
    kp1, des1 = orb.detectAndCompute(query_img, None)

    results = []  # Store match results

    # Iterate over dataset images
    for dataset_image_path in dataset_image_paths:
        try:
            # Load dataset image
            dataset_img = cv2.imread(dataset_image_path, cv2.IMREAD_GRAYSCALE)
            # Remove alpha channel if present
            if dataset_img.shape[-1] == 4:
                print("Removing alpha channel")
                dataset_img = cv2.cvtColor(dataset_img, cv2.COLOR_BGRA2BGR)
            if dataset_img is None:
                raise ValueError(f"Dataset image at {dataset_image_path} not found.")

            # Detect and compute features for dataset image
            kp2, des2 = orb.detectAndCompute(dataset_img, None)
            if des2 is None:
                continue

            # Use Brute-Force matcher with Hamming distance
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

            # Find matches
            matches = bf.knnMatch(des1, des2, k=2)
            # print(f"{matches[0]=}")
            # Remove tuples with len 1
            matches = [m for m in matches if len(m) == 2]

            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:  # Ratio test threshold
                    good_matches.append(m)

            # If sufficient matches, use RANSAC to handle occlusions
            if len(good_matches) > 10:  # Minimum matches for reliable homography
                src_pts = np.float32(
                    [kp1[m.queryIdx].pt for m in good_matches]
                ).reshape(-1, 1, 2)
                dst_pts = np.float32(
                    [kp2[m.trainIdx].pt for m in good_matches]
                ).reshape(-1, 1, 2)

                # Compute homography
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                inliers = np.sum(mask)  # Count inliers
            else:
                M, mask, inliers = None, None, 0

            # Store the result for this dataset image
            results.append(
                {
                    "dataset_image_path": dataset_image_path,
                    "good_matches": len(good_matches),
                    "inliers": inliers,
                    "homography": M,
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            print(f"{kp2=} {des2=}")
            print(f"{dataset_image_path=}")

    return results


# Visualize matches (optional)
def visualize_matches(query_image_path, dataset_image_path, kp1, kp2, matches, mask):
    query_img = cv2.imread(query_image_path, cv2.IMREAD_GRAYSCALE)
    dataset_img = cv2.imread(dataset_image_path, cv2.IMREAD_GRAYSCALE)

    matched_img = cv2.drawMatches(
        query_img,
        kp1,
        dataset_img,
        kp2,
        matches,
        None,
        matchesMask=mask.ravel().tolist(),
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    plt.figure(figsize=(15, 10))
    plt.imshow(matched_img)
    plt.axis("off")
    plt.show()


# Example Usage
query_image = "red.png"
dataset_images = glob("giant/*.png")

results = match_images(query_image, dataset_images)

# Display the best match
best_match = max(results, key=lambda x: x["inliers"])
print("Best Match:", best_match)
