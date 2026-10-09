OCLP_PRESERVED_PATHS=(
  ".github/"
  "opencore_legacy_patcher/custom/"
  "opencore_legacy_patcher/__init__.py"
  "ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper"
  "README.md"
  "README_CN.md"
  "LICENSE"
)

oclp_upstream_pathspec() {
  OCLP_UPSTREAM_PATHSPEC=(.)
  local preserved_path
  for preserved_path in "${OCLP_PRESERVED_PATHS[@]}"; do
    OCLP_UPSTREAM_PATHSPEC+=(":(exclude)$preserved_path")
  done
}
