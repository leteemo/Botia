from node.Node import Node
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import pyautogui


class GetSearchedImageCoordNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'GetSearchedImageCoordNode'       # Nom du noeud

    def __init__(self):
        super(GetSearchedImageCoordNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input', multi_input=True)
        self.add_output('output')
        self.add_output('data')
        
        self.add_text_input('name_image', label='name', tooltip=None, tab=None)

        self.botManager = None

        self.value = None


    def action(self):

        query = self.get_property('name_image')

        image_urls = bing_image_search(query, num_images=2)

        # Download the first image
        image, is_downloaded = download_image(image_urls[1]) if image_urls else (None, False)

        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        if is_downloaded and image is not None:
            orb = cv2.ORB_create()
            keypoints1, descriptors1 = orb.detectAndCompute(screenshot_cv, None)
            keypoints2, descriptors2 = orb.detectAndCompute(image, None)

            # FLANN configuration
            FLANN_INDEX_LSH = 6
            index_params = dict(algorithm=FLANN_INDEX_LSH,
                                table_number=6,
                                key_size=12,
                                multi_probe_level=1)
            search_params = dict(checks=50)

            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(descriptors1, descriptors2, k=2)

            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for match in matches:
                if len(match) == 2:
                    m, n = match
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)


            if len(good_matches) >= 5:

                # Calculate the coordinates of the matched keypoints
                src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)


                points_x = filter_points_by_std(src_pts[:, 0, 0])
                points_y = filter_points_by_std(src_pts[:, 0, 1])

                center_x = np.mean(points_x)
                center_y = np.mean(points_y)


                # Draw the matches
                img_matches = cv2.drawMatches(image, keypoints1, screenshot_cv, keypoints2, good_matches, None)

                # Resize for display
                new_width = 900
                new_height = 600
                img_matches = cv2.resize(img_matches, (new_width, new_height))
                pyautogui.moveTo(center_x, center_y)
                # Display the matches
                print(f"Coordinates of the center of the matched image: ({center_x:.2f}, {center_y:.2f})")
            else:
                print("Not enough good matches found to determine coordinates.")
        else:
            print("No valid image downloaded.")


        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        setattr(self.get_output("data"), 'data', self.value)


def filter_points_by_std(points, threshold=1.0):

    # Calculer la moyenne et l'écart type des points
    mean = np.mean(points)
    std_dev = np.std(points)
    
    # Créer un masque pour filtrer les points dont l'écart à la moyenne est inférieur à threshold * std_dev
    filtered_mask = np.abs(points - mean) <= threshold * std_dev
    
    # Retourner les points filtrés
    return points[filtered_mask]

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_array = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is not None:
            return image, True
        else:
            print("Error: the image could not be decoded.")
    else:
        print("Error while downloading the image:", response.status_code)
    return None, False

def bing_image_search(query, num_images=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    query = query.replace(' ', '+')
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1&tsc=ImageBasicHover"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Error during request:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    image_tags = soup.find_all('a', {'class': 'iusc'})
    
    image_urls = []
    for tag in image_tags[:num_images]:
        m = tag.get('m')
        if m:
            m_dict = eval(m)
            image_urls.append(m_dict.get('murl'))
    
    return image_urls




