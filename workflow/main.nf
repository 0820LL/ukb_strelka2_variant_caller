// Declare syntax version
nextflow.enable.dsl=2

process STRELKA_SOMATIC {

    container = "${projectDir}/../singularity-images/depot.galaxyproject.org-singularity-strelka-2.9.10--h9ee0642_1.img"

    input:
    path fasta
    path fasta_index
    path tumor_cram 
    path tumor_cram_index
    path normal_cram 
    path normal_cram_index
    val prefix

    output:
    path "*.somatic_indels.vcf.gz"
    path "*.somatic_indels.vcf.gz.tbi"
    path "*.somatic_snvs.vcf.gz"
    path "*.somatic_snvs.vcf.gz.tbi"


    script:
    """
    configureStrelkaSomaticWorkflow.py \\
        --tumor $tumor_cram \\
        --normal $normal_cram \\
        --referenceFasta $fasta \\
        --runDir strelka
    
    python strelka/runWorkflow.py -m local -j ${params.thread_num}

    mv strelka/results/variants/somatic.indels.vcf.gz     ${prefix}.somatic_indels.vcf.gz
    mv strelka/results/variants/somatic.indels.vcf.gz.tbi ${prefix}.somatic_indels.vcf.gz.tbi
    mv strelka/results/variants/somatic.snvs.vcf.gz       ${prefix}.somatic_snvs.vcf.gz
    mv strelka/results/variants/somatic.snvs.vcf.gz.tbi   ${prefix}.somatic_snvs.vcf.gz.tbi

    cp ${prefix}.somatic_indels.vcf.gz ${launchDir}/${params.outdir}/
    cp ${prefix}.somatic_indels.vcf.gz.tbi ${launchDir}/${params.outdir}/
    cp ${prefix}.somatic_snvs.vcf.gz ${launchDir}/${params.outdir}/
    cp ${prefix}.somatic_snvs.vcf.gz.tbi ${launchDir}/${params.outdir}/
    """
}

workflow{
    fasta             = Channel.of(params.fasta)
    fasta_index       = Channel.of(params.fasta_index)
    tumor_cram        = Channel.of(params.tumor_cram)
    tumor_cram_index  = Channel.of(params.tumor_cram_index)
    normal_cram       = Channel.of(params.normal_cram)
    normal_cram_index = Channel.of(params.normal_cram_index)
    prefix            = Channel.of(params.prefix)
    STRELKA_SOMATIC(fasta, fasta_index, tumor_cram, tumor_cram_index, normal_cram, normal_cram_index, prefix)
}

