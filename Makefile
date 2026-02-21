.PHONY: all install download copy service restart uninstall

INSTALL_DIR   = /usr/local/lib/local_dashboard
SERVICE_SRC   = local-dashboard.service
SERVICE_DST   = /etc/systemd/system/local-dashboard.service
STATIC_DIR    = static
FONTS_DIR     = $(STATIC_DIR)/fonts

MONO_BASE     = https://fonts.gstatic.com/s/ibmplexmono
SANS_BASE     = https://fonts.gstatic.com/s/ibmplexsans

all: install

# ── Full install ───────────────────────────────────────────────────────────────
install: download copy service restart
	@echo ""
	@echo "  ✓ local-dashboard is running at http://127.0.0.1:47652/"
	@echo "  Use 'make logs' to follow logs, 'make uninstall' to remove."

# ── Step 1: download assets ────────────────────────────────────────────────────
download:
	@echo "→ Downloading Tailwind CSS..."
	@curl -sL https://cdn.tailwindcss.com -o $(STATIC_DIR)/tailwind.js
	@echo "→ Downloading IBM Plex Mono fonts..."
	@mkdir -p $(FONTS_DIR)
	@curl -sL "$(MONO_BASE)/v19/-F63fjptAgt5VM-kVkqdyU8n1iIq131nj-otFQ.woff2" \
		-o $(FONTS_DIR)/IBMPlexMono-Regular.woff2
	@curl -sL "$(MONO_BASE)/v19/-F6pfjptAgt5VM-kVkqdyU8n3vAO4_ha1RIW.woff2" \
		-o $(FONTS_DIR)/IBMPlexMono-Medium.woff2
	@curl -sL "$(MONO_BASE)/v19/-F6qfjptAgt5VM-kVkqdyU8n3uNAOa_ha2Re.woff2" \
		-o $(FONTS_DIR)/IBMPlexMono-SemiBold.woff2
	@echo "→ Downloading IBM Plex Sans fonts..."
	@curl -sL "$(SANS_BASE)/v21/zYX9KVElMYYaJe8bpLHnCwDKhd26.woff2" \
		-o $(FONTS_DIR)/IBMPlexSans-Regular.woff2
	@curl -sL "$(SANS_BASE)/v21/zYX8KVElMYYaJe8bpLHnCwDKhdTmdKZM.woff2" \
		-o $(FONTS_DIR)/IBMPlexSans-Medium.woff2
	@curl -sL "$(SANS_BASE)/v21/zYX8KVElMYYaJe8bpLHnCwDKhdTumdKZM.woff2" \
		-o $(FONTS_DIR)/IBMPlexSans-SemiBold.woff2
	@echo "✓ Assets downloaded."

# ── Step 2: copy package ───────────────────────────────────────────────────────
copy:
	@echo "→ Installing package to $(INSTALL_DIR)..."
	@sudo mkdir -p $(INSTALL_DIR)
	@sudo cp -r . $(INSTALL_DIR)/
	@echo "✓ Package installed."

# ── Step 3: install service ────────────────────────────────────────────────────
service:
	@echo "→ Installing systemd service..."
	@sudo cp $(SERVICE_SRC) $(SERVICE_DST)
	@sudo systemctl daemon-reload
	@sudo systemctl enable local-dashboard
	@echo "✓ Service installed and enabled."

# ── Step 4: restart ────────────────────────────────────────────────────────────
restart:
	@echo "→ Starting local-dashboard..."
	@sudo systemctl restart local-dashboard
	@sleep 1
	@sudo systemctl is-active --quiet local-dashboard \
		&& echo "✓ Service is running." \
		|| (echo "✗ Service failed to start. Run 'make logs'." && exit 1)

# ── Helpers ────────────────────────────────────────────────────────────────────
logs:
	journalctl -u local-dashboard -f

status:
	sudo systemctl status local-dashboard

# ── Uninstall ──────────────────────────────────────────────────────────────────
uninstall:
	@echo "→ Stopping and disabling service..."
	@sudo systemctl disable --now local-dashboard || true
	@sudo rm -f $(SERVICE_DST)
	@sudo systemctl daemon-reload
	@echo "→ Removing package..."
	@sudo rm -rf $(INSTALL_DIR)
	@echo "✓ Uninstalled."
