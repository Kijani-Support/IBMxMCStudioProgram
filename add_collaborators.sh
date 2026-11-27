#!/usr/bin/env bash
# Invite the IBM Dev Day participants as collaborators on the repo.
# Usage:  gh auth login            (once, with an account that is an admin of the repo)
#         bash add_collaborators.sh [owner/repo] [permission]
# Defaults: Kijani-Support/IBMxMCStudioProgram, push (write) access.
# Each user gets an email invite that they must accept.
set -u

REPO="${1:-Kijani-Support/IBMxMCStudioProgram}"
PERMISSION="${2:-push}"   # pull | triage | push | maintain | admin

USERS=(
  SagwaM
  loiceolum-art
  Mercywafula196
  MUGOHILLARY
  mson-wagz
  Blessings-ux
  okellojun
  reeny-ai
  markle-art
  emmanuel-haro
  zixxiyu
  chinonso-victor001
  Faqih001
  Mr-JMuli
  briangitz
  uservkai
  ChrisDamian
  Juniormaina
  ElderNuel
  Bart-codes
  robatemesgen209
  DanOkothDev
  victormutune
)

ok=0; fail=0
for u in "${USERS[@]}"; do
  if gh api --silent -X PUT "repos/${REPO}/collaborators/${u}" -f permission="${PERMISSION}"; then
    echo "invited  ${u}"; ok=$((ok+1))
  else
    echo "FAILED   ${u}"; fail=$((fail+1))
  fi
done
echo "Done: ${ok} invited, ${fail} failed (repo: ${REPO}, permission: ${PERMISSION})"
