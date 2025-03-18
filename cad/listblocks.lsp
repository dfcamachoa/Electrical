(defun c:ListBlocks ()
  (vl-load-com)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq modelSpace (vla-get-ModelSpace doc))
  (setq filename "C:/Users/dcamachoav/Documents/Python/Electrical/cad/temp_output.txt")  ; Temporary file for each DWG
  (setq file (open filename "w"))

  (if file
    (progn
      (setq filepath (vla-get-FullName doc))
      (setq shortfilename (vl-filename-base filepath))
      (vlax-for entity modelSpace
        (if (eq (vla-get-ObjectName entity) "AcDbBlockReference")
          (progn
            (setq block (vla-get-EffectiveName entity))
            (setq layer (vla-get-Layer entity))
            (write-line (strcat shortfilename";"layer";"block) file)
          )
        )
      )
      (close file)
      (princ (strcat "\nInformation saved to " filename))
    )
    (princ "\nError: Unable to open file for writing.")
  )
  (princ)
)