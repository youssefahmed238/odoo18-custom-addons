/** @odoo-module */
import PortalSidebar from "@portal/js/portal_sidebar";

PortalSidebar.include({
    printPdf(url) {
        let iframe = "";
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.className = 'pdfIframe'
            document.body.appendChild(iframe);
            iframe.style.display = 'none';
            iframe.onload = function () {
                setTimeout(function () {
                    iframe.focus();
                    iframe.contentWindow.print();
                    URL.revokeObjectURL(url)
                }, 1);
            };
        }
        iframe.src = url;
    }
});