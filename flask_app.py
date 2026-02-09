from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- HOMEPAGE (Library) ---
LIBRARY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Study Library</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; margin: 0; padding: 50px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; max-width: 1000px; margin: 0 auto; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-decoration: none; color: #2c3e50; transition: 0.3s; border-top: 6px solid #63b3ed; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>My Study Library</h1>
    <div class="grid">
        {% for book in books %}
        <a href="/study/{{ book }}" class="card"><h2>📚 {{ book|capitalize }}</h2></a>
        {% endfor %}
    </div>
</body>
</html>
"""

# --- STUDY PORTAL ---
STUDY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; display: flex; height: 100vh; font-family: 'Inter', sans-serif; background: #f0f2f5; overflow: hidden; }
        #sidebar { width: 320px; margin: 20px; background: rgba(44, 62, 80, 0.98); color: white; display: flex; flex-direction: column; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: all 0.4s ease; position: relative; }
        #sidebar.hidden { margin-left: -350px; opacity: 0; pointer-events: none; }
        .header { padding: 20px; background: rgba(26, 37, 47, 0.5); text-align: center; color: #63b3ed; font-weight: bold; border-radius: 15px 15px 0 0; }
        .home-btn { display: block; padding: 10px; text-align: center; color: #bdc3c7; text-decoration: none; font-size: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1); }
        #toc-container { flex: 1; overflow-y: auto; padding: 10px; }
        .toc-link { display: block; padding: 12px 15px; color: #bdc3c7; text-decoration: none; cursor: pointer; border-radius: 8px; margin-bottom: 3px; }
        .toc-link:hover { background: rgba(255,255,255,0.1); color: white; }
        .toc-link.active { background: #63b3ed !important; color: white !important; font-weight: bold; }
        .toc-h2 { padding-left: 35px; font-size: 0.85rem; display: none; background: rgba(0,0,0,0.1); }
        .toc-h1 { font-weight: bold; color: #fff; }
        #toggle-btn { position: fixed; bottom: 30px; left: 30px; width: 50px; height: 50px; background: #2c3e50; color: white; border: none; border-radius: 50%; cursor: pointer; z-index: 100; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        #content { flex: 1; overflow-y: auto; background: transparent; transition: all 0.4s; }
        
        /* BANNER IS NOW HIDDEN BY DEFAULT */
        #banner-wrapper { display: none; width: 100%; height: 350px; background: #000; border-radius: 0 0 15px 15px; overflow: hidden; }
        
        #display-area { max-width: 850px; margin: 20px auto; padding: 40px; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 60vh; line-height: 1.7; }

        /* --- NEW: MAIN CONTENT IMAGE FEATURE STYLE --- */
        .img-feature-container { 
            margin: 40px auto; 
            text-align: center; 
            cursor: pointer;
            display: block;
        }
        .img-feature-container img { 
            max-width: 100%; 
            height: auto;
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
            transition: transform 0.3s ease, box-shadow 0.3s ease; 
        }
        .img-feature-container:hover img { 
            transform: scale(1.02); 
            box-shadow: 0 15px 40px rgba(0,0,0,0.2); 
        }
        .click-hint { 
            display: block; 
            margin-top: 15px; 
            font-size: 0.9rem; 
            font-weight: bold; 
            color: #63b3ed; 
            background: rgba(99, 179, 237, 0.1);
            padding: 5px 15px;
            border-radius: 20px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }

        .force-bold { font-weight: 900 !important; color: #000 !important; }
        .force-italic { font-style: italic !important; }
        #display-area table { width: 100% !important; border-collapse: collapse; margin: 25px 0; border: 1px solid #edf2f7 !important; }
        #display-area td, #display-area th { padding: 12px; border: 1px solid #edf2f7 !important; }
        
        .nav-controls { display: flex; justify-content: space-between; max-width: 850px; margin: 20px auto 50px auto; }
        .nav-btn { padding: 12px 25px; background: #2c3e50; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .nav-btn:disabled { opacity: 0.3; }
        #lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; cursor: zoom-out; justify-content: center; align-items: center; }
        #lightbox img { max-width: 95%; max-height: 95%; }
        #hidden-loader { display: none; }
    </style>
</head>
<body>
    <button id="toggle-btn" onclick="toggleSidebar()">☰</button>
    <div id="lightbox" onclick="this.style.display='none'"><img id="lightbox-img" src=""></div>
    <div id="sidebar">
        <a href="/" class="home-btn">← Back to Library</a>
        <div class="header">{{ subject|upper }}</div>
        <div id="toc-container"></div>
    </div>
    <div id="content">
        <div id="banner-wrapper"><img id="chapter-banner-img" src=""></div>
        <div id="display-area"><h1 style="text-align:center; color:#ccc; margin-top:100px;">Select a Topic</h1></div>
        <div class="nav-controls">
            <button id="prev-btn" class="nav-btn" onclick="navigate(-1)">← Prev</button>
            <button id="next-btn" class="nav-btn" onclick="navigate(1)">Next →</button>
        </div>
    </div>
    <iframe id="hidden-loader" src="/doc/{{ subject }}"></iframe>

    <script>
        const loader = document.getElementById('hidden-loader');
        const tocContainer = document.getElementById('toc-container');
        const displayArea = document.getElementById('display-area');
        let allItems = [];
        let currentIdx = -1;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('hidden'); }

        loader.onload = function() {
            const doc = loader.contentDocument || loader.contentWindow.document;
            const headings = Array.from(doc.querySelectorAll('h1, h2'));
            headings.forEach((heading, index) => {
                const link = document.createElement('a');
                link.textContent = heading.innerText;
                const tag = heading.tagName.toLowerCase();
                link.className = 'toc-link toc-' + tag;
                link.onclick = () => { if (tag === 'h1') expandModule(link); loadSection(index); };
                tocContainer.appendChild(link);
                allItems.push({ heading, link, tag });
            });
            updateNavButtons();
        };

        function expandModule(h1Link) {
            document.querySelectorAll('.toc-h2').forEach(h2 => h2.style.display = 'none');
            let next = h1Link.nextElementSibling;
            while (next && next.classList.contains('toc-h2')) {
                next.style.display = 'block';
                next = next.nextElementSibling;
            }
        }

        function loadSection(index) {
            if (index < 0 || index >= allItems.length) return;
            currentIdx = index;
            document.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
            const current = allItems[index];
            current.link.classList.add('active');
            
            displayArea.innerHTML = '';
            const section = document.createElement('div');
            const contentSource = current.heading;
            
            function processNode(node) {
                const clone = node.cloneNode(true);
                const sourceElements = node.querySelectorAll ? [node, ...node.querySelectorAll('*')] : [node];
                const cloneElements = clone.querySelectorAll ? [clone, ...clone.querySelectorAll('*')] : [clone];
                sourceElements.forEach((el, i) => {
                    if (!el.style) return;
                    const style = window.getComputedStyle(el);
                    const target = cloneElements[i];
                    if (parseInt(style.fontWeight) >= 600 || style.fontWeight === 'bold') target.classList.add('force-bold');
                    if (style.fontStyle === 'italic') target.classList.add('force-italic');
                });
                return clone;
            }

            section.appendChild(processNode(contentSource));
            let next = contentSource.nextElementSibling;
            while (next && !['H1', 'H2'].includes(next.tagName)) {
                section.appendChild(processNode(next));
                next = next.nextElementSibling;
            }

            // --- THE IMAGE FEATURE INJECTOR ---
            const allImages = section.querySelectorAll('img');
            allImages.forEach(img => {
                const fileName = img.getAttribute('src').split('/').pop();
                const fullPath = '/study/{{ subject }}/images/' + fileName;
                
                // Wrap image in a feature container
                const container = document.createElement('div');
                container.className = 'img-feature-container';
                
                // Create the Click Hint
                const hint = document.createElement('div');
                hint.className = 'click-hint';
                hint.innerHTML = "🔍 Click image to enlarge";

                // Setup Image
                img.src = fullPath;
                
                // Update DOM structure
                img.parentNode.insertBefore(container, img);
                container.appendChild(img);
                container.appendChild(hint);

                // Make Clickable
                container.onclick = () => {
                    document.getElementById('lightbox-img').src = fullPath;
                    document.getElementById('lightbox').style.display = 'flex';
                };
            });

            displayArea.appendChild(section);
            document.getElementById('content').scrollTop = 0;
            updateNavButtons();
        }

        function navigate(direction) { loadSection(currentIdx + direction); }
        function updateNavButtons() {
            document.getElementById('prev-btn').disabled = (currentIdx <= 0);
            document.getElementById('next-btn').disabled = (currentIdx >= allItems.length - 1 || currentIdx === -1);
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def library():
    books = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and os.path.exists(os.path.join(BASE_DIR, d, 'guide.html'))]
    return render_template_string(LIBRARY_HTML, books=sorted(books))

@app.route('/study/<subject>')
def study_portal(subject):
    return render_template_string(STUDY_HTML, subject=subject)

@app.route('/doc/<subject>')
def serve_doc(subject):
    return send_from_directory(os.path.join(BASE_DIR, subject), 'guide.html')

@app.route('/study/<subject>/images/<path:filename>')
def serve_subject_images(subject, filename):
    directory = os.path.join(BASE_DIR, subject, 'images')
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(debug=True)