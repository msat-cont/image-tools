(define (simple-ela infilename tmpfilename outfilename quality)
  (let* ((img (car (gimp-file-load RUN-NONINTERACTIVE infilename infilename)))
         (draw (car (gimp-image-get-active-layer img)))
         (draw-aux 0)
         ;(error-layer 0)
    )
    ; first we need to save the image in a lower quality into a temporary file
    (file-jpeg-save RUN-NONINTERACTIVE img draw tmpfilename tmpfilename quality 0 0 0 "GIMP ELA Temporary Image" 0 0 0 0)
    ; we re-read the image that has the lower quality from the temporary file into an auxiliary layer
    (set! draw-aux (car(gimp-file-load-layer RUN-NONINTERACTIVE img tmpfilename)))
    ; and we delete the temporary file
    (file-delete tmpfilename)
    ; we add the auxiliary layer at the top of the image
    (gimp-image-add-layer img draw-aux -1)
    ; we set this top (auxiliary) layer to be used at a difference mode
    (gimp-layer-set-mode draw-aux DIFFERENCE-MODE)
    ; by now, we could (in the interactive mode) see the ELA view (based on two overlaid layers)

    ; now we either take the current visible (i.e. ELA) view
    ;(gimp-edit-copy-visible img)
    ; and copy it into another layer that contains the ELA view; thus we have the ELA view in a single layer
    ;(set! error-layer (car (gimp-layer-new-from-visible img img "Error Levels") ))
    ; we put this new layer at the top of the image
    ;(gimp-image-add-layer img error-layer -1)
    ; we re-balance white-black levels of this final level
    ;(gimp-levels-stretch error-layer)
    ; and we save the final layer
    ;(gimp-file-save RUN-NONINTERACTIVE img error-layer outfilename outfilename)

    ; or we can use the current image without new layers adedd, but we need to flatten it, so that we have a single layer
    (gimp-image-flatten img)
    ; we read id of this (flattened) result layer
    (set! draw (car (gimp-image-get-active-layer img)))
    ; we re-balance white-black levels of the (flattened) layer
    (gimp-levels-stretch draw)
    ; and we save that (flattened) layer
    (gimp-file-save RUN-NONINTERACTIVE img draw outfilename outfilename)

    ; we clean-up via deleting the image from gimp memory
    (gimp-image-delete img)
  )
)
