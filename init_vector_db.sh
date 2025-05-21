#!/bin/bash
set -euo pipefail

create_db_if_not_exists() {
  local dbname=$1
  local user="postgres"

  echo "Checking if database '$dbname' exists..."
  if psql -U "$user" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$dbname'" | grep -q 1; then
    echo "Database '$dbname' already exists. Skipping."
  else
    echo "Creating database '$dbname'..."
    if psql -U "$user" -d postgres -c "CREATE DATABASE \"$dbname\";"; then
      echo "Database '$dbname' created successfully."
      echo "Creating extension 'vector' in database '$dbname'..."
      if psql -U "$user" -d "$dbname" -c "CREATE EXTENSION IF NOT EXISTS vector;"; then
        echo "Extension 'vector' created successfully in '$dbname'."
      else
        echo "Warning: Failed to create extension 'vector' in '$dbname'."
      fi
    else
      echo "Error: Failed to create database '$dbname'. Skipping."
    fi
  fi
}

databases=(
  "vectors"
)

for db in "${databases[@]}"; do
  while ! create_db_if_not_exists "$db"; do
    echo "Retrying creation of database '$db'..."
    sleep 2
  done
done

echo "All database operations completed successfully."
