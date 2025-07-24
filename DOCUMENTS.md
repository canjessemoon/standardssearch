# Document Sources

This application searches through military and aerospace standards documents. Due to GitHub file size limitations, the PDF documents are not included in this repository.

## Required Documents

To use this application, you need to place the following PDF files in the `backend/documents/` directory:

1. **MIL-HDBK-759B.pdf** (~7 MB)
   - Title: Military Handbook - Human Engineering Design Criteria for Military Systems, Equipment and Facilities
   - Source: [Defense Technical Information Center](https://www.dtic.mil/)

2. **MIL-STD-1472H.pdf** (~12 MB)
   - Title: Human Engineering
   - Source: [Defense Technical Information Center](https://www.dtic.mil/)

3. **MIL-STD-1474D.pdf** (~0.8 MB)
   - Title: Noise Limits
   - Source: [Defense Technical Information Center](https://www.dtic.mil/)

4. **MIL-STD-882E.pdf** (~1.1 MB)
   - Title: System Safety
   - Source: [Defense Technical Information Center](https://www.dtic.mil/)

5. **NASA-STD-3000B_VOL-1.pdf** (~25 MB)
   - Title: Space Flight Human-System Standard Volume 1
   - Source: [NASA Technical Standards](https://standards.nasa.gov/)

## Setup Instructions

1. Create the documents directory:
   ```bash
   mkdir -p backend/documents
   ```

2. Download the required PDFs from their official sources
3. Place all PDF files in the `backend/documents/` directory
4. Run the application - it will automatically index the documents on startup

## Alternative Test Documents

If you cannot access the original documents, you can test the application with any PDF files by placing them in the `backend/documents/` directory. The application will index and search any PDF documents it finds.

## Legal Notice

These documents are published by the U.S. Department of Defense and NASA and are in the public domain. Please ensure you download them from official government sources.
