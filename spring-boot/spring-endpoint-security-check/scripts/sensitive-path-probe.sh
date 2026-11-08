#!/usr/bin/env bash
# sensitive-path-probe.sh
#
# Read-only check for commonly exposed sensitive paths.
# GET requests only. No writes. No auth bypass. No fuzzing.
#
# USE ONLY ON HOSTS YOU OWN OR HAVE WRITTEN PERMISSION TO TEST.
#
# usage:
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu --parallel 10
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu --timeout 5 --ips 300
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu --skip-ratelimit
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu --delay 0.5
#   ./sensitive-path-probe.sh https://schneaggchat.lerchenflo.eu --delay 1 --parallel 1
#
# outputs:
#   probe-results-<ts>.tsv        code, size, content-type, redirect, path
#   probe-ratelimit-<ts>.txt      one status per line (unless --skip-ratelimit)
#
# exit:
#   0  all probes were 404/403/401/429/000 or SPA fallback
#   2  at least one non-404/403/401/429/000 that is not an SPA fallback
#   1  usage error
#
# requires: bash 4+, curl, awk, xargs, seq, sort, uniq

set -uo pipefail

usage() {
  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 1
}

[[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]] && usage
TARGET="${1%/}"; shift
[[ "$TARGET" =~ ^https?:// ]] || TARGET="https://$TARGET"

PARALLEL=6
TIMEOUT=10
SKIP_RATELIMIT=0
IPS_COUNT=250
IPS_PARALLEL=20
DELAY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --parallel)       PARALLEL="${2:-6}";       shift 2 ;;
    --timeout)        TIMEOUT="${2:-10}";       shift 2 ;;
    --delay)          DELAY="${2:-0}";          shift 2 ;;
    --skip-ratelimit) SKIP_RATELIMIT=1;         shift ;;
    --ips)            IPS_COUNT="${2:-250}";    shift 2 ;;
    --ips-parallel)   IPS_PARALLEL="${2:-20}";  shift 2 ;;
    -h|--help)        usage ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
done

# --delay throttles the path scan only (the rate-limit burst stays unthrottled
# on purpose). With --parallel N > 1 the pause is per-worker, so the effective
# gap between requests is DELAY/N; use --parallel 1 for a strict serial delay.
[[ "$DELAY" =~ ^[0-9]+([.][0-9]+)?$ ]] || { echo "--delay must be a number (seconds), got: $DELAY" >&2; exit 1; }

command -v curl >/dev/null || { echo "curl required" >&2; exit 1; }

TS=$(date +%Y%m%d-%H%M%S)
RESULTS="probe-results-$TS.tsv"
RL_RESULTS="probe-ratelimit-$TS.txt"

# ---------------------------------------------------------------------------
# Path list. Comments (#) and blank lines are stripped before probing.
# Group 1: exact paths observed in the 2026-11-08 scanner log.
# Group 2: additional high-signal paths.
# ---------------------------------------------------------------------------

PATHS_RAW=$(cat <<'EOF'
# ---- exact paths from the log ----
/admin-panel/.env
/control-panel/.env
/user-panel/.env
/node/.env
/express/.env
/next/.env
/nuxt/.env
/react/.env
/nest/.env
/vue/.env
/angular/.env
/vite/.env
/svelte/.env
/backup/.env
/backups/.env
/old/.env
/tmp/.env
/temp/.env
/cronlab/.env
/cron/.env
/lab/.env
/en/.env
/psnlink/.env
/exapi/.env
/administrator/.env
/sitemaps/.env
/logs/.env
/cache/.env
/mailer/.env
/mail/.env
/email/.env
/mailing/.env
/notifications/.env
/smtp/.env
/sender/.env
/campaign/.env
/newsletter/.env
/ses/.env
/sendgrid/.env
/sparkpost/.env
/postmark/.env
/mandrill/.env
/mailjet/.env
/brevo/.env
/mailgun/.env
/transactional/.env
/bulk/.env
/aws/.env
/gcp/.env
/cloud/.env
/docker/.env
/azure/.env
/k8s/.env
/kubernetes/.env
/terraform/.env
/infrastructure/.env
/ansible/.env
/.git/.env
/cd/.env
/jenkins/.env
/gitlab/.env
/actions/.env
/ci/.env
/circleci/.env
/travis/.env
/buildkite/.env
/github/.env
/mysql/.env
/mongodb/.env
/redis/.env
/elasticsearch/.env
/kafka/.env
/postgres/.env
/queue/.env
/rabbitmq/.env
/job/.env
/test/.env
/qa/.env
/preview/.env
/worker/.env
/beta/.env
/uat/.env
/stage/.env
/development/.env
/production/.env
/config/app/.env
/.env.backup1
/.env.backup2

/phpinfo.php
/info.php
/php.php
/i.php
/pi.php
/test.php
/phpinfo
/p.php
/debug.php
/pinfo.php
/admin/phpinfo.php
/test/phpinfo.php
/old/phpinfo.php
/tmp/phpinfo.php
/public/phpinfo.php
/info
/dev/phpinfo.php
/php-info.php
/phpversion.php
/old_phpinfo.php
/server-info.php
/_profiler/phpinfo
/_phpinfo.php
/_environment
/webroot/index.php/_environment
/mail/phpinfo.php
/cpanel/phpinfo.php
/server-status.php
/hosting/phpinfo.php
/webmail/phpinfo.php
/smtp/phpinfo.php
/phpinfo.php.bak
/phpinfo.php.old
/info.php.bak
/phpinfo.php.save
/staging/phpinfo.php
/beta/phpinfo.php
/uat/phpinfo.php
/qa/phpinfo.php
/phpinfo.php~
/www/phpinfo.php
/htdocs/phpinfo.php
/public_html/phpinfo.php
/site/phpinfo.php
/docs/phpinfo.php
/wp-admin/phpinfo.php
/preview/phpinfo.php
/core/phpinfo.php
/includes/phpinfo.php
/administrator/phpinfo.php

/service-account.json
/sa.json
/gcp-key.json
/gcp-credentials.json
/credentials.json
/google-credentials.json
/.config/gcloud/application_default_credentials.json
/application_default_credentials.json
/gcp-sa.json
/key.json
/keyfile.json
/firebase-adminsdk.json
/google-key.json
/firebase-key.json

# ---- additional .env variants ----
/.env
/.env.local
/.env.production
/.env.development
/.env.prod
/.env.dev
/.env.staging
/.env.test
/.env.example
/.env.bak
/.env.old
/.env.save
/.env~
/.env.swp
/.env.dist
/.env.ci
/.env.dev.local

# ---- vcs metadata ----
/.git/config
/.git/HEAD
/.git/index
/.git/logs/HEAD
/.gitignore
/.svn/entries
/.svn/wc.db
/.hg/hgrc

# ---- os / editor junk ----
/.DS_Store
/.htaccess
/.htpasswd
/.idea/workspace.xml
/.vscode/settings.json

# ---- app configs ----
/wp-config.php
/wp-config.php.bak
/wp-config.php.old
/wp-config.php.save
/config.php
/configuration.php
/settings.php
/local.settings.php
/config/database.yml
/database.yml
/secrets.yml
/config.yml
/docker-compose.yml
/docker-compose.yaml
/Dockerfile
/Makefile

# ---- cloud / ssh keys ----
/.aws/credentials
/.aws/config
/id_rsa
/.ssh/id_rsa
/.ssh/id_dsa
/.ssh/id_ecdsa
/.ssh/authorized_keys

# ---- db dumps / backups ----
/backup.sql
/dump.sql
/database.sql
/db.sql
/db_backup.sql
/mysqldump.sql
/backup.zip
/backup.tar.gz
/backup.tar
/www.zip
/site.zip
/htdocs.zip
/public_html.zip
/public.zip

# ---- server status / debug ----
/server-status
/server-info
/actuator/env
/actuator/heapdump
/actuator/health

# ---- api docs / consoles ----
/swagger.json
/swagger-ui.html
/api-docs
/v2/api-docs
/v3/api-docs
/openapi.json
/openapi.yaml
/graphql
/graphiql
/adminer.php
/phpmyadmin
/pma
/myadmin
/mysqladmin
/console

# ---- package manifests ----
/package.json
/package-lock.json
/yarn.lock
/composer.json
/composer.lock
/Gemfile
/Gemfile.lock
/requirements.txt
/go.mod

# ---- spring boot actuator (this backend is kotlin + spring) ----
/actuator
/actuator/beans
/actuator/configprops
/actuator/mappings
/actuator/metrics
/actuator/loggers
/actuator/threaddump
/actuator/httptrace
/actuator/httpexchanges
/actuator/prometheus
/actuator/info
/actuator/scheduledtasks
/actuator/caches
/actuator/conditions
/actuator/sessions
/actuator/flyway
/actuator/liquibase
/actuator/startup
/actuator/shutdown
/jolokia
/jolokia/list
# ---- spring boot 1.x / unprefixed actuator ----
/env
/beans
/configprops
/mappings
/metrics
/health
/info
/trace
/httptrace
/heapdump
/threaddump
/dump
/loggers
/shutdown
# ---- jvm app config / packaging ----
/application.properties
/application.yml
/application.yaml
/application-dev.yml
/application-dev.properties
/application-prod.yml
/application-prod.properties
/application-local.yml
/application-local.properties
/bootstrap.yml
/bootstrap.properties
/WEB-INF/web.xml
/WEB-INF/classes/application.properties
/WEB-INF/classes/application.yml
/META-INF/MANIFEST.MF
/h2-console
/error

# ---- firebase / mobile backend (fcm push, app config) ----
/google-services.json
/GoogleService-Info.plist
/firebase.json
/.firebaserc
/firebase-debug.log
/serviceAccountKey.json
/fcm.json
/.well-known/assetlinks.json
/.well-known/apple-app-site-association

# ---- framework secrets (rails / django / laravel / .net) ----
/config/master.key
/config/credentials.yml.enc
/config/secrets.yml
/settings.py
/local_settings.py
/db.sqlite3
/storage/logs/laravel.log
/telescope/requests
/appsettings.json
/appsettings.Development.json
/web.config

# ---- ci / deploy configs ----
/.gitlab-ci.yml
/.travis.yml
/.circleci/config.yml
/azure-pipelines.yml
/Jenkinsfile
/bitbucket-pipelines.yml
/.github/workflows/deploy.yml
/.drone.yml
/Procfile
/vercel.json
/netlify.toml
/now.json

# ---- ftp / remote-deploy plugin creds (plaintext) ----
/sftp-config.json
/.ftpconfig
/ftp-config.json
/deployment-config.json
/.remote-sync.json
/.vscode/sftp.json
/WS_FTP.ini

# ---- shell / tool dotfiles with secrets ----
/.npmrc
/.dockercfg
/.docker/config.json
/.netrc
/.pgpass
/.my.cnf
/.git-credentials
/.gitconfig
/.bash_history
/.zsh_history
/.python_history
/.mysql_history
/.s3cfg
/.kube/config
/.vault-token

# ---- more secrets / env ----
/secrets.json
/secret.json
/vault.json
/.env.vault
/.env.keys
/.env.production.local
/credentials
/secrets

# ---- state / dumps / db files ----
/dump.rdb
/redis.conf
/terraform.tfstate
/terraform.tfstate.backup
/.terraform/terraform.tfstate
/database.sqlite
/db.sqlite
/app.db
/data.db
/backup.tar.bz2
/backup.rar
/site.tar.gz
/latest.sql
/users.sql
/data.sql

# ---- logs ----
/app.log
/error.log
/debug.log
/application.log
/spring.log
/server.log
/access.log
/npm-debug.log
/yarn-error.log

# ---- api consoles / debug (framework-specific) ----
/swagger-ui/index.html
/swagger-resources
/v3/api-docs/swagger-config
/playground
/altair
/debug/pprof
/debug/pprof/heap
/debug/pprof/goroutine

# ---- info files (usually public, but flagged as [PUBLIC] if 200) ----
/robots.txt
/sitemap.xml
/.well-known/security.txt
/crossdomain.xml
EOF
)

PATHS=$(sed -e 's/#.*//' -e 's/[[:space:]]*$//' -e '/^$/d' <<< "$PATHS_RAW" | sort -u)
N_PATHS=$(wc -l <<< "$PATHS")
# space-separated (awk -v cannot hold literal newlines); none of these contain spaces
PUBLIC_PATHS='robots.txt sitemap.xml .well-known/security.txt crossdomain.xml .well-known/assetlinks.json .well-known/apple-app-site-association'

# ---------------------------------------------------------------------------
# Probe one URL. Emits a TSV line: code  size  content_type  redirect  path
# ---------------------------------------------------------------------------
probe() {
  local url="$1" out
  out=$(curl -sS -k -o /dev/null --max-redirs 0 -m "$TIMEOUT" \
              -A "sensitive-path-probe/1.0 (+$TARGET)" \
              -w '%{http_code}\t%{size_download}\t%{content_type}\t%{redirect_url}' \
              "$url" 2>/dev/null) || out=$'000\t0\t\t'
  printf '%s\t%s\n' "$out" "${url#"$TARGET"}"
  [[ "$DELAY" != "0" ]] && sleep "$DELAY"
  return 0
}
export -f probe
export TIMEOUT TARGET DELAY

trap 'echo; echo "Interrupted. Partial results in $RESULTS"; exit 130' INT

echo "== sensitive-path-probe =="
echo "target:   $TARGET"
echo "paths:    $N_PATHS"
echo "parallel: $PARALLEL   timeout: ${TIMEOUT}s   delay: ${DELAY}s"
echo "results:  $RESULTS"
echo

# ---------------------------------------------------------------------------
# Real-client-IP check — run FIRST, before probing trips the rate limiter,
# otherwise this request just gets a 429 and never reaches the app log.
# 203.0.113.7 is RFC 5737 TEST-NET-3, reserved for documentation (not a real host).
# ---------------------------------------------------------------------------
XFF_IP="203.0.113.7"
echo "== X-Forwarded-For / real-client-IP check =="
echo "sending one request with 'X-Forwarded-For: $XFF_IP'."
echo "then check your app log: does it see $XFF_IP, or a proxy IP?"
echo "if it sees a proxy IP, per-IP rate limits and fail2ban cannot"
echo "distinguish real attackers behind that proxy."
echo
curl -sS -k -o /dev/null -m 10 --max-redirs 0 \
     -H "X-Forwarded-For: $XFF_IP" \
     -A "sensitive-path-probe-xff/1.0 (+$TARGET)" \
     -w 'HTTP %{http_code}, %{size_download} bytes\n' \
     "$TARGET/" 2>/dev/null || echo "(request failed)"
echo

echo "$PATHS" \
  | xargs -P "$PARALLEL" -I{} bash -c 'probe "$@"' _ "$TARGET{}" \
  > "$RESULTS" 2>/dev/null || true

# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------
echo "== status distribution =="
awk -F'\t' '{print $1}' "$RESULTS" | sort | uniq -c | sort -rn
echo

SPA_HINT=$(awk -F'\t' '$1=="200" && $3 ~ /^text\/html/' "$RESULTS" | wc -l)
if (( SPA_HINT > 20 )); then
  echo "NOTE: $SPA_HINT paths returned 200 + text/html. This is almost certainly"
  echo "      an SPA/HTML catch-all. Those 200s are FALSE POSITIVES - the file"
  echo "      is not actually served, only the app shell is. They are tagged"
  echo "      [SPA?] below; compare sizes and content-types to confirm."
  echo
fi

echo "== findings (not 404/403/401/429/000) =="
FINDINGS=$(awk -F'\t' -v pub="$PUBLIC_PATHS" '
BEGIN {
  n = split(pub, a, " ")
  for (i = 1; i <= n; i++) { p = a[i]; sub(/^\//, "", p); pubmap[p] = 1 }
}
{
  code = $1; size = $2; ctype = $3; redir = $4; path = $5
  if (code == "404" || code == "403" || code == "401" || code == "429" || code == "000") next
  bare = path; sub(/^\//, "", bare)
  if (code == "200" || code == "206") {
    if (bare in pubmap)               label = "[PUBLIC]  "
    else if (ctype ~ /^text\/html/)   label = "[SPA?]    "
    else                              label = "[EXPOSED?]"
  } else if (code ~ /^3/)             label = "[REDIR]   "
  else                                label = "[OTHER]   "
  printf "%-10s %s\t%8s bytes\t%-30s\t%s%s\n", label, code, size, ctype, path,
         (redir != "" ? "  -> " redir : "")
}
' "$RESULTS" | sort -k2,2 -k5,5)

if [[ -z "$FINDINGS" ]]; then
  echo "(none - every path returned 404, 403, 401, 429, or was unreachable)"
  RC=0
else
  echo "$FINDINGS"
  echo
  echo "  by label:"
  echo "$FINDINGS" | awk '{print $1}' | sort | uniq -c
  RC=2
fi
echo

# ---------------------------------------------------------------------------
# Rate-limit burst
# ---------------------------------------------------------------------------
if (( SKIP_RATELIMIT )); then
  echo "== rate-limit check skipped (--skip-ratelimit) =="
else
  echo "== rate-limit check: firing $IPS_COUNT requests at /.env =="
  echo "   expect mostly 404/403, then 429 once the limiter trips."
  echo
  seq 1 "$IPS_COUNT" | xargs -P "$IPS_PARALLEL" -I{} \
    curl -sS -k -o /dev/null -m 5 --max-redirs 0 \
         -A "sensitive-path-probe-rl/1.0 (+$TARGET)" \
         -w '%{http_code}\n' \
         "$TARGET/.env?probe={}" 2>/dev/null \
    | tee "$RL_RESULTS" >/dev/null

  echo "== rate-limit distribution =="
  sort "$RL_RESULTS" | uniq -c | sort -rn
  echo
  echo "full list: $RL_RESULTS"
fi
echo

# ---------------------------------------------------------------------------
# Wrap up
# ---------------------------------------------------------------------------
echo "== done =="
echo "raw results: $RESULTS"
[[ -s "${RL_RESULTS:-/dev/null}" ]] && echo "rate-limit:  $RL_RESULTS"
echo
echo "legend:"
echo "  [PUBLIC]   200 on robots.txt / sitemap.xml / security.txt - expected"
echo "  [SPA?]     200 + text/html on a sensitive path - almost certainly the"
echo "             app shell, NOT a real leak. Verify by comparing the size to"
echo "             your index.html."
echo "  [EXPOSED?] 200 with non-HTML body on .env / *.json / phpinfo - investigate"
echo "  [REDIR]    3xx - check the redirect target; a login page is fine, a"
echo "             direct download path is not"
echo "  [OTHER]    anything else (5xx, 4xx not in {403,404,429})"
echo
echo "if any [EXPOSED?] appears: rotate the secret immediately, then add an"
echo "explicit deny rule at the edge (return 404, not 403, to avoid signalling"
echo "that the path exists)."

exit "$RC"