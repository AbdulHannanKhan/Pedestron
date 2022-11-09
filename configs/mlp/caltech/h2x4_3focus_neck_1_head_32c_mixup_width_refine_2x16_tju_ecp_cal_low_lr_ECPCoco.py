# model settings
model = dict(
    type='CSP',
    pretrained='open-mmlab://msra/hrnetv2_w32',
    backbone=dict(
        type='HRNet',
        extra=dict(
            stage1=dict(
                num_modules=1,
                num_branches=1,
                block='BOTTLENECK',
                num_blocks=(4,),
                num_channels=(64,)),
            stage2=dict(
                num_modules=1,
                num_branches=2,
                block='BASIC',
                num_blocks=(4, 4),
                num_channels=(32, 64)),
            stage3=dict(
                num_modules=4,
                num_branches=3,
                block='BASIC',
                num_blocks=(4, 4, 4),
                num_channels=(32, 64, 128)),
            stage4=dict(
                num_modules=3,
                num_branches=4,
                block='BASIC',
                num_blocks=(4, 4, 4, 4),
                fuse_till=3,
                num_channels=(32, 64, 128, 256))
        ),
        # frozen_stages=-1,
        norm_eval=False,
    ),
    neck=dict(
        type='MLPFPN',
        in_channels=[32, 64, 128, 256],
        out_channels=32,
        mixer_count=1,
        start_stage=2,
        end_stage=3,
        feat_channels=[4, 16, 128]
    ),
    bbox_head=dict(
        type='CSPMLPHead',
        num_classes=2,
        in_channels=32,
        windowed_input=True,
        patch_dim=8,
        width=480,
        height=640,
        predict_width=True,
        stacked_convs=1,
        feat_channels=32,
        strides=[4],
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=0.01),
        loss_bbox=dict(type='IoULoss', loss_weight=0.05),
        loss_offset=dict(
            type='CrossEntropyLoss', use_sigmoid=True, loss_weight=0.1)),
    refine_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(type='RoIAlign', out_size=7, sample_num=2),
        out_channels=32,
        featmap_strides=[4]
    ),
    refine_head=dict(
        type='RefineHead',
        num_cls_fcs=2,
        num_cls_convs=2,
        use_gm=True,
        in_channels=32,
        conv_out_channels=32,
        fc_out_channels=1024,
        alpha=0.5,
        dropout_prob=0.5,
        weight_decay=0.0005,
        roi_feat_size=7,
        loss_cls=dict(
            type='CrossEntropyLoss', use_sigmoid=True, loss_weight=1.0),
        ),
)
# training and testing settings

train_cfg = dict(
    rcnn=dict(
        assigner=dict(
            type='MaxIoUAssigner',
            pos_iou_thr=0.5,
            neg_iou_thr=0.5,
            min_pos_iou=0.5,
            rescale_labels=False,
            soft_labels=False,
            ignore_iof_thr=-1),
        sampler=dict(
            type='RandomSampler',
            num=512,
            pos_fraction=0.25,
            neg_pos_ub=-1,
            add_gt_as_proposals=True),
        pos_weight=2,
        debug=True
    ),
    csp_head=dict(
        nms_pre=1000,
        min_bbox_size=0,
        score_thr=0.1,  # 0.2, #0.05,
        nms=dict(type='nms', iou_thr=0.7),
        max_per_img=100,
    )
)

test_cfg = dict(
    csp_head=dict(
        nms_pre=1000,
        min_bbox_size=0,
        score_thr=0.001, #0.2, #0.05,
        nms=dict(type='nms', iou_thr=0.5),
        max_per_img=100,
    ),
)

# dataset settings
dataset_type = 'ECPCocoDataset'
data_root = './datasets/Caltech/train_images/'
INF = 1e8
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
data = dict(
    imgs_per_gpu=16,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        ann_file='./datasets/Caltech/train_m.json',
        img_prefix=data_root,
        mixup=True,
        img_scale=(640, 480),
        img_norm_cfg=img_norm_cfg,
        small_box_to_ignore=False,
        size_divisor=32,
        flip_ratio=0.5,
        with_mask=False,
        with_crowd=True,
        with_label=True,
        with_width=True,
        remove_small_box=True,
        small_box_size=8,
        strides=[4],
        regress_ranges=((-1, INF),)),
    val=dict(
        type=dataset_type,
        ann_file='./datasets/Caltech/val.json',
        img_prefix=data_root,
        #img_scale=(1333, 800),
        img_scale=(640, 480),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        with_width=True,
        flip_ratio=0,
        with_mask=False,
        with_crowd=False,
        with_label=True),
    test=dict(
        type=dataset_type,
        ann_file='./datasets/Caltech/val.json',
        img_prefix=data_root,
        img_scale=(640, 480),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0,
        with_width=True,
        with_mask=False,
        with_crowd=False,
        with_label=False,
        test_mode=True))
# optimizer
# optimizer = dict(
#     type='SGD',
#     lr=0.01/10,
#     momentum=0.9,
#     weight_decay=0.0001,
#     paramwise_options=dict(bias_lr_mult=2., bias_decay_mult=0.))
mean_teacher = True
optimizer = dict(
    type='Adam',
    lr=2e-4,
)
# optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
optimizer_config = dict(mean_teacher = dict(alpha=0.999))
# learning policy
lr_config = dict(
    policy='step',
    warmup='constant',
    warmup_iters=5000,
    warmup_ratio=1.0 / 3,
    gamma=0.3,
    step=[120])

checkpoint_config = dict(interval=1)
evaluation = dict(interval=1, eval_hook='CocoDistEvalMRHook')
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings

wandb = dict(
    init_kwargs=dict(
        project="caltech",
        entity="mlpthesis",
        name="nh_hr_2x32_mixup_width_refine_2x16_tju_ecp_low_lr_ECPCoco",
        config=dict(
            work_dirs="${work_dir}",
            total_step="${runner.max_epochs}",
            ),
        ),
        interval=50,
    )

total_epochs = 80
device_ids = range(4)
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = '/netscratch/hkhan/work_dirs/mlpod/caltech/NH_HR2x32_mixup_width_refine_2x16_tju_ecp_low_lr_ECPCoco/'
# load_from = None
load_from = '/netscratch/hkhan/work_dirs/mlpod/ecp/NH_HR_mixup_width_refine_tju_ecp_no_crowd/epoch_112.pth'
resume_from = None
# resume_from = '/home/ljp/code/mmdetection/work_dirs/csp4_mstrain_640_800_x101_64x4d_fpn_gn_2x/epoch_10.pth'
workflow = [('train', 1)]
