import sanitizeHtml from "sanitize-html";

const defaultOptions: sanitizeHtml.IOptions = {
    allowedTags: sanitizeHtml.defaults.allowedTags.filter((tag) => tag !== "pre").concat("img","code"),
    allowedAttributes: {
        a: ["href"],
        img: ["src", "alt", "width", "height"],
    },
    allowedIframeHostnames: ["www.youtube.com"],
};

const handleLineEndings = (html: string) => {
    return html.replace(/<pre>([\s\S]*?)<\/pre>/g, (match, p1) => {
        return `<pre>${p1.replace(/\n+/g, '<br>')}</pre>`;
    });
};

const sanitize = (
  dirty: string,
  options: sanitizeHtml.IOptions | undefined
) => ({
  __html: sanitizeHtml(handleLineEndings(dirty), { ...defaultOptions, ...options }),
});

interface SanitizeHTMLProps {
  html: string;
  options?: sanitizeHtml.IOptions;
}

export const SanitizeHTML = ({ html, options }: SanitizeHTMLProps) => (
  <div dangerouslySetInnerHTML={sanitize(html, options)} />
);
