# Settings Page - Simple Fix

## Problem
Frontend sending invalid 'jp' language → Backend rejecting with 400

## Root Cause
Old cached data with 'jp' value keeps getting re-sent

## Simple Solution
Send ONLY changed fields, not entire object

## Implementation
See: phase-2/frontend/src/app/settings/page-simple.tsx
